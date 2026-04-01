"""
core/orchestrator.py

Main workflow engine for the vendor security review platform.

Responsibilities:
- Accept a review request (vendor name, optional URL, optional documents)
- Coordinate all downstream steps in the correct order:
    1. Create a run folder via FolderManager
    2. Check robots.txt and ToS if a URL is provided
    3. Trigger dynamic scraping if scraping is permitted
    4. Ingest any provided or scraped documents via DocumentProcessor
    5. Run Claude-powered security analysis via SecurityReviewer
    6. Write a structured findings report to the run folder
    7. Post results back to a TeamDynamix ticket via TDXClient
- Provide status callbacks / logging throughout the run
- Support both synchronous (CLI) and asynchronous (FastAPI webhook) invocation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class ReviewRequest:
    """Encapsulates all inputs needed to kick off a vendor security review."""

    vendor_name: str
    """Human-readable vendor name (used for folder naming and report headers)."""

    vendor_url: Optional[str] = None
    """Optional homepage or security-page URL to scrape."""

    document_paths: list[Path] = field(default_factory=list)
    """Paths to documents already on disk (PDFs, DOCX, etc.) to include."""

    tdx_ticket_id: Optional[str] = None
    """If set, findings will be posted back to this TeamDynamix ticket."""


@dataclass
class ReviewResult:
    """Captures the outcome of a completed vendor security review."""

    run_folder: Path
    """Path to the folder containing all artifacts for this run."""

    findings_report_path: Optional[Path] = None
    """Path to the generated findings report Markdown file."""

    risk_score: Optional[float] = None
    """Numeric risk score (0.0 = lowest risk, 10.0 = highest risk)."""

    summary: Optional[str] = None
    """Short human-readable summary of the review outcome."""

    tdx_comment_posted: bool = False
    """True if findings were successfully posted to the TDX ticket."""


class Orchestrator:
    """
    Drives end-to-end vendor security review runs.

    Usage::

        orchestrator = Orchestrator()
        result = orchestrator.run(ReviewRequest(vendor_name="Acme", vendor_url="https://acme.example.com"))
    """

    def __init__(self) -> None:
        """Initialize the orchestrator and its sub-component instances."""
        pass

    def run(self, request: ReviewRequest) -> ReviewResult:
        """
        Execute a full vendor security review synchronously.

        Steps:
        1. Create run folder
        2. Scrape vendor site (if URL provided and permitted)
        3. Ingest documents
        4. Perform security analysis
        5. Write report
        6. Update TDX ticket (if ticket ID provided)

        Args:
            request: A ReviewRequest containing all inputs for this run.

        Returns:
            A ReviewResult with paths to artifacts and a summary of findings.
        """
        pass

    async def run_async(self, request: ReviewRequest) -> ReviewResult:
        """
        Execute a full vendor security review asynchronously.

        Intended for use as a FastAPI background task or when triggered
        by a webhook from TeamDynamix.

        Args:
            request: A ReviewRequest containing all inputs for this run.

        Returns:
            A ReviewResult with paths to artifacts and a summary of findings.
        """
        pass

    def _run_scraping_phase(self, request: ReviewRequest, run_folder: Path) -> list[Path]:
        """
        Check robots.txt and ToS, then scrape the vendor site if permitted.

        Args:
            request: The current review request.
            run_folder: The output folder for this run.

        Returns:
            List of paths to documents downloaded or extracted during scraping.
        """
        pass

    def _run_analysis_phase(self, document_paths: list[Path], run_folder: Path) -> ReviewResult:
        """
        Process documents and run Claude-powered security analysis.

        Args:
            document_paths: All documents collected for this review.
            run_folder: The output folder for this run.

        Returns:
            A partially populated ReviewResult with findings and risk score.
        """
        pass
