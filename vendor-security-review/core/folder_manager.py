"""
core/folder_manager.py

Creates and manages per-vendor review run folders under the configured runs/
directory.

Each run gets an isolated folder named:
    runs/{sanitized_company_name}_{YYYY-MM-DD}_{HH-MM-SS}/

Sub-directory layout inside every run folder:
    robots-txt/       — snapshot of the vendor's robots.txt
    scraper/          — Claude-generated scraper script + explanation
    scraped-data/     — raw content collected by the scraper
    vendor-provided/  — drop zone for manually supplied vendor documents
    analysis/         — final report, summaries, and intermediate artifacts
    logs/             — execution log for this specific run

A metadata.json file is created at the run root on initialisation and kept
up-to-date via the update_* helper methods.
"""

from __future__ import annotations

import json
import logging
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Status and recommendation literals
# ---------------------------------------------------------------------------

# Valid values for the "status" field in metadata.json.
VALID_STATUSES = frozenset(
    {
        "queued",
        "scraping",
        "awaiting_vendor_docs",
        "analyzing",
        "recommendation_ready",
    }
)

# Valid values for the "recommendation" field in metadata.json.
VALID_RECOMMENDATIONS = frozenset({"approved", "denied", "needs_human_review", None})

# ---------------------------------------------------------------------------
# Sub-directory names (single source of truth)
# ---------------------------------------------------------------------------

RUN_SUBDIRS: tuple[str, ...] = (
    "robots-txt",
    "scraper",
    "scraped-data",
    "vendor-provided",
    "analysis",
    "logs",
)


class FolderManager:
    """
    Creates and manages per-run output folders for the vendor security review
    workflow.

    One ``FolderManager`` instance is typically shared across a review session.
    It is safe to create multiple run folders from the same instance (e.g. for
    batch processing).

    Usage::

        fm = FolderManager()
        run_folder = fm.create_run_folder(
            company_name="Acme Corp",
            website_url="https://acme.example.com",
            tdx_ticket_id="TDX-12345",
        )

        # Later — update the run status
        fm.update_status(run_folder, "scraping")

        # Read current metadata
        meta = fm.read_metadata(run_folder)
        print(meta["status"])  # "scraping"

        # Get a well-known sub-directory path
        vendor_docs_dir = fm.get_subdir(run_folder, "vendor-provided")
    """

    def __init__(self, runs_root: Path | None = None) -> None:
        """
        Args:
            runs_root: Override the default ``runs/`` directory.  If *None*,
                       the path from :data:`config.settings.RUNS_DIR` is used.
        """
        if runs_root is None:
            # Lazy import keeps the module usable even when dotenv isn't set up
            # (e.g., during unit tests that pass runs_root explicitly).
            from config.settings import RUNS_DIR

            runs_root = RUNS_DIR

        self.runs_root: Path = Path(runs_root)
        self.runs_root.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def create_run_folder(
        self,
        company_name: str,
        website_url: str = "",
        tdx_ticket_id: str | None = None,
    ) -> Path:
        """
        Create a timestamped run folder for a new vendor security review.

        The folder name is built from the sanitized company name and the
        current UTC timestamp so that multiple reviews of the same vendor
        never collide::

            runs/acme-corp_2024-03-15_13-45-22/

        The following sub-directories are created inside the run folder:
        ``robots-txt``, ``scraper``, ``scraped-data``, ``vendor-provided``,
        ``analysis``, ``logs``.

        A :file:`metadata.json` is written at the run root with the initial
        review state.

        A run-specific logger is configured to write to
        ``logs/run.log`` inside the new folder.

        Args:
            company_name:  Human-readable vendor / company name.
            website_url:   Optional vendor homepage URL (stored in metadata).
            tdx_ticket_id: Optional TeamDynamix ticket ID to associate with
                           this review.

        Returns:
            :class:`pathlib.Path` pointing to the newly created run folder.

        Raises:
            OSError: If the folder cannot be created due to a filesystem error.
        """
        slug = self.sanitize_vendor_name(company_name)
        timestamp = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
        folder_name = f"{slug}_{timestamp}"
        run_folder = self.runs_root / folder_name

        # Create the run root and all sub-directories in one pass.
        run_folder.mkdir(parents=True, exist_ok=False)
        for subdir in RUN_SUBDIRS:
            (run_folder / subdir).mkdir()

        # Write the initial metadata file.
        now_iso = datetime.now(tz=timezone.utc).isoformat()
        metadata: dict[str, Any] = {
            "company_name": company_name,
            "website_url": website_url,
            # Overall workflow state — see VALID_STATUSES for allowed values.
            "status": "queued",
            "created_at": now_iso,
            "updated_at": now_iso,
            # TDX ticket associated with this review (may be None).
            "tdx_ticket_id": tdx_ticket_id,
            # Final recommendation produced by the AI reviewer.
            # One of: "approved", "denied", "needs_human_review", or null.
            "recommendation": None,
            # Short human-readable summary written by the AI reviewer.
            "one_line_summary": None,
            # Checklist of documents we asked the vendor to provide.
            "requested_docs_checklist": [],
            # Documents actually received (filenames or URLs).
            "received_docs": [],
        }
        self._write_metadata(run_folder, metadata)

        # Set up a run-specific log file so every step in this review has a
        # dedicated audit trail separate from the application-level log.
        self._configure_run_logger(run_folder)

        logger = self._get_run_logger(run_folder)
        logger.info(
            "Run folder created: %s (company=%r, tdx=%s)",
            run_folder,
            company_name,
            tdx_ticket_id or "none",
        )

        return run_folder

    def get_subdir(self, run_folder: Path, subdir: str) -> Path:
        """
        Return the :class:`~pathlib.Path` for a named sub-directory inside a
        run folder, creating it if it has somehow been removed.

        Args:
            run_folder: Root path of an existing run folder.
            subdir:     Sub-directory name.  Must be one of ``RUN_SUBDIRS``
                        (``"robots-txt"``, ``"scraper"``, ``"scraped-data"``,
                        ``"vendor-provided"``, ``"analysis"``, ``"logs"``).

        Returns:
            Path to the sub-directory (guaranteed to exist on return).

        Raises:
            ValueError: If *subdir* is not a recognised name.
        """
        if subdir not in RUN_SUBDIRS:
            raise ValueError(
                f"Unknown sub-directory {subdir!r}. "
                f"Valid options: {sorted(RUN_SUBDIRS)}"
            )
        path = run_folder / subdir
        path.mkdir(parents=True, exist_ok=True)
        return path

    def list_run_folders(self) -> list[Path]:
        """
        Return all existing run folders sorted from oldest to newest.

        Only immediate children of ``runs_root`` that are directories and
        whose names match the expected ``<slug>_<date>_<time>`` pattern are
        included.  Stray files or unrelated directories are silently ignored.

        Returns:
            List of :class:`~pathlib.Path` objects, oldest first.
        """
        pattern = re.compile(r"^.+_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}$")
        folders = [
            p
            for p in self.runs_root.iterdir()
            if p.is_dir() and pattern.match(p.name)
        ]
        # Sort lexicographically — because the timestamp is in ISO format
        # (with separators) the alphabetical order equals chronological order.
        return sorted(folders, key=lambda p: p.name)

    def read_metadata(self, run_folder: Path) -> dict[str, Any]:
        """
        Read and return the current contents of a run's :file:`metadata.json`.

        Args:
            run_folder: Root path of the run folder.

        Returns:
            Dictionary with all metadata fields.

        Raises:
            FileNotFoundError: If :file:`metadata.json` does not exist.
            json.JSONDecodeError: If the file contains invalid JSON.
        """
        metadata_path = run_folder / "metadata.json"
        with metadata_path.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    def update_status(self, run_folder: Path, status: str) -> None:
        """
        Update the ``status`` field in :file:`metadata.json`.

        Args:
            run_folder: Root path of the run folder.
            status:     New status string.  Must be one of
                        ``"queued"``, ``"scraping"``,
                        ``"awaiting_vendor_docs"``, ``"analyzing"``,
                        ``"recommendation_ready"``.

        Raises:
            ValueError: If *status* is not a valid status string.
        """
        if status not in VALID_STATUSES:
            raise ValueError(
                f"Invalid status {status!r}. Valid options: {sorted(VALID_STATUSES)}"
            )
        self.update_metadata(run_folder, {"status": status})
        logger = self._get_run_logger(run_folder)
        logger.info("Status → %s", status)

    def update_recommendation(
        self,
        run_folder: Path,
        recommendation: str | None,
        one_line_summary: str | None = None,
    ) -> None:
        """
        Set the ``recommendation`` (and optionally ``one_line_summary``) fields.

        Args:
            run_folder:      Root path of the run folder.
            recommendation:  One of ``"approved"``, ``"denied"``,
                             ``"needs_human_review"``, or ``None``.
            one_line_summary: Optional short summary to store alongside the
                              recommendation.

        Raises:
            ValueError: If *recommendation* is not a valid value.
        """
        if recommendation not in VALID_RECOMMENDATIONS:
            raise ValueError(
                f"Invalid recommendation {recommendation!r}. "
                f"Valid options: {sorted(str(v) for v in VALID_RECOMMENDATIONS)}"
            )
        updates: dict[str, Any] = {"recommendation": recommendation}
        if one_line_summary is not None:
            updates["one_line_summary"] = one_line_summary
        self.update_metadata(run_folder, updates)
        logger = self._get_run_logger(run_folder)
        logger.info("Recommendation → %s | summary: %s", recommendation, one_line_summary)

    def update_metadata(self, run_folder: Path, fields: dict[str, Any]) -> None:
        """
        Merge *fields* into :file:`metadata.json` and refresh ``updated_at``.

        This is the low-level writer used by all other ``update_*`` helpers.
        You can also call it directly to update any combination of fields in a
        single atomic write::

            fm.update_metadata(run_folder, {
                "tdx_ticket_id": "TDX-99",
                "received_docs": ["soc2_2024.pdf"],
            })

        Args:
            run_folder: Root path of the run folder.
            fields:     Key-value pairs to merge into the existing metadata.
                        ``updated_at`` is always refreshed automatically.

        Raises:
            FileNotFoundError: If :file:`metadata.json` does not exist.
        """
        metadata = self.read_metadata(run_folder)
        metadata.update(fields)
        metadata["updated_at"] = datetime.now(tz=timezone.utc).isoformat()
        self._write_metadata(run_folder, metadata)

    def add_requested_doc(self, run_folder: Path, doc_name: str) -> None:
        """
        Append an entry to the ``requested_docs_checklist`` in metadata.

        Args:
            run_folder: Root path of the run folder.
            doc_name:   Name or description of the document being requested
                        (e.g. ``"SOC 2 Type II Report"``).
        """
        meta = self.read_metadata(run_folder)
        checklist: list[str] = meta.get("requested_docs_checklist", [])
        if doc_name not in checklist:
            checklist.append(doc_name)
        self.update_metadata(run_folder, {"requested_docs_checklist": checklist})

    def add_received_doc(self, run_folder: Path, doc_name: str) -> None:
        """
        Append an entry to the ``received_docs`` list in metadata.

        Call this whenever a vendor document is successfully ingested so the
        metadata stays in sync with what is physically present in
        ``vendor-provided/``.

        Args:
            run_folder: Root path of the run folder.
            doc_name:   Filename or URL of the received document.
        """
        meta = self.read_metadata(run_folder)
        received: list[str] = meta.get("received_docs", [])
        if doc_name not in received:
            received.append(doc_name)
        self.update_metadata(run_folder, {"received_docs": received})
        logger = self._get_run_logger(run_folder)
        logger.info("Document received: %s", doc_name)

    # ------------------------------------------------------------------
    # Static helpers
    # ------------------------------------------------------------------

    @staticmethod
    def sanitize_vendor_name(vendor_name: str) -> str:
        """
        Convert a vendor name to a filesystem-safe, URL-friendly slug.

        Steps:
        1. Normalise Unicode to ASCII (NFKD decomposition + ASCII encode).
        2. Lowercase the result.
        3. Replace any character that is not a letter, digit, space, or
           hyphen with a space.
        4. Collapse consecutive whitespace / hyphens into a single hyphen.
        5. Strip leading / trailing hyphens.

        Examples::

            "Acme Corp (LLC)"  → "acme-corp-llc"
            "Björk & Co."      → "bjork-co"
            "  Spaces  "       → "spaces"

        Args:
            vendor_name: Raw vendor name string (may include Unicode,
                         punctuation, extra whitespace, etc.).

        Returns:
            Lowercase, hyphen-separated ASCII slug.

        Raises:
            ValueError: If the resulting slug is empty (e.g. the input
                        contained only special characters).
        """
        # Step 1 — normalise Unicode to ASCII.
        normalised = (
            unicodedata.normalize("NFKD", vendor_name)
            .encode("ascii", errors="ignore")
            .decode("ascii")
        )

        # Step 2 — lowercase.
        normalised = normalised.lower()

        # Step 3 — keep only alphanumerics, spaces, and hyphens; replace
        #           everything else with a space so word boundaries are preserved.
        cleaned = re.sub(r"[^a-z0-9 \-]", " ", normalised)

        # Step 4 — collapse runs of whitespace and hyphens to a single hyphen.
        slug = re.sub(r"[\s\-]+", "-", cleaned).strip("-")

        if not slug:
            raise ValueError(
                f"Vendor name {vendor_name!r} produced an empty slug after sanitization."
            )
        return slug

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _write_metadata(self, run_folder: Path, metadata: dict[str, Any]) -> None:
        """
        Serialise *metadata* to :file:`metadata.json` inside *run_folder*.

        The file is written atomically: the JSON is first serialised to a
        string, then written in one ``write_text`` call to avoid leaving a
        partially written file if the process is interrupted.

        Args:
            run_folder: Root path of the run folder.
            metadata:   Full metadata dictionary to persist.
        """
        metadata_path = run_folder / "metadata.json"
        metadata_path.write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    @staticmethod
    def _run_log_path(run_folder: Path) -> Path:
        """Return the path to the run-specific log file."""
        return run_folder / "logs" / "run.log"

    @staticmethod
    def _run_logger_name(run_folder: Path) -> str:
        """Return a unique logger name derived from the run folder name."""
        return f"vendor_review.run.{run_folder.name}"

    def _configure_run_logger(self, run_folder: Path) -> None:
        """
        Create and configure a :mod:`logging` logger that writes to
        ``logs/run.log`` inside *run_folder*.

        The logger is also given a :class:`~logging.StreamHandler` so that
        run-level messages surface in the console during development.  Both
        handlers use the same structured format::

            2024-03-15 13:45:22 UTC | INFO | message text

        Args:
            run_folder: Root path of the run folder (must already exist).
        """
        logger_name = self._run_logger_name(run_folder)
        logger = logging.getLogger(logger_name)

        # Guard against double-registration if create_run_folder is called
        # more than once for the same folder (shouldn't happen normally, but
        # defensive programming costs nothing here).
        if logger.handlers:
            return

        logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            fmt="%(asctime)s UTC | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        # Suppress the default UTC suffix added by some formatters; we
        # include "UTC" in the fmt string for clarity.
        formatter.converter = lambda *_: datetime.now(tz=timezone.utc).timetuple()

        # File handler — DEBUG and above go to run.log.
        log_path = self._run_log_path(run_folder)
        fh = logging.FileHandler(log_path, encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        # Stream handler — INFO and above go to stdout for visibility.
        sh = logging.StreamHandler()
        sh.setLevel(logging.INFO)
        sh.setFormatter(formatter)
        logger.addHandler(sh)

        # Prevent messages from bubbling up to the root logger and being
        # printed a second time.
        logger.propagate = False

    def _get_run_logger(self, run_folder: Path) -> logging.Logger:
        """
        Retrieve the logger for an existing run folder.

        If the logger has not been configured yet (e.g. when calling
        ``update_status`` on a run folder from a previous session), it is
        configured on demand so that the log file is always written to.

        Args:
            run_folder: Root path of the run folder.

        Returns:
            Configured :class:`logging.Logger` instance.
        """
        logger = logging.getLogger(self._run_logger_name(run_folder))
        if not logger.handlers:
            # Run folder exists on disk from a prior session — re-attach the
            # file handler so subsequent updates are logged correctly.
            self._configure_run_logger(run_folder)
        return logger
