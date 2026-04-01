"""
core/folder_manager.py

Creates and manages per-run output folders under the configured runs/ directory.

Each vendor review run gets an isolated folder named:
    runs/<sanitized-vendor-name>-<YYYYMMDD-HHMMSS>/

Within a run folder the following structure is created automatically:
    raw_docs/     — original documents as downloaded/received
    processed/    — normalized text extracted from documents
    reports/      — final findings report and any intermediate artifacts
    scraper/      — HTML snapshots and scraped content from the vendor site
    logs/         — per-run log files
"""

from __future__ import annotations

from pathlib import Path


class FolderManager:
    """
    Manages the lifecycle of per-run output folders.

    Usage::

        fm = FolderManager()
        run_folder = fm.create_run_folder("Acme Corp")
        docs_dir = fm.get_subdir(run_folder, "raw_docs")
    """

    # Sub-directories created inside every run folder.
    RUN_SUBDIRS: tuple[str, ...] = ("raw_docs", "processed", "reports", "scraper", "logs")

    def __init__(self, runs_root: Path | None = None) -> None:
        """
        Args:
            runs_root: Override the default runs/ directory. If None, the path
                       from config.settings.RUNS_DIR is used.
        """
        pass

    def create_run_folder(self, vendor_name: str) -> Path:
        """
        Create a timestamped folder for a new vendor review run.

        The folder name is derived from the vendor name (sanitized for the
        filesystem) and the current UTC timestamp, e.g.:
            runs/acme-corp-20240315-134522/

        All standard sub-directories (raw_docs, processed, etc.) are created
        within the new run folder.

        Args:
            vendor_name: Human-readable vendor name.

        Returns:
            Path to the newly created run folder.
        """
        pass

    def get_subdir(self, run_folder: Path, subdir: str) -> Path:
        """
        Return the path to a named sub-directory within a run folder.

        Args:
            run_folder: Root path of the run folder.
            subdir: Name of the sub-directory (must be one of RUN_SUBDIRS).

        Returns:
            Path to the sub-directory (guaranteed to exist).

        Raises:
            ValueError: If subdir is not a recognised sub-directory name.
        """
        pass

    def list_run_folders(self) -> list[Path]:
        """
        Return a sorted list of all existing run folders (oldest first).

        Returns:
            List of Path objects for each run folder under runs_root.
        """
        pass

    @staticmethod
    def sanitize_vendor_name(vendor_name: str) -> str:
        """
        Convert a vendor name to a filesystem-safe slug.

        E.g. "Acme Corp (LLC)" -> "acme-corp-llc"

        Args:
            vendor_name: Raw vendor name string.

        Returns:
            Lowercase, hyphen-separated slug with special characters removed.
        """
        pass
