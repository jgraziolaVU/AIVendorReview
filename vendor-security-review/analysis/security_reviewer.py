"""
analysis/security_reviewer.py

Claude-powered security analysis engine.

Responsibilities:
- Accept processed document text from DocumentProcessor
- Construct targeted prompts that evaluate vendor security posture against
  a configurable framework (default: NIST CSF 2.0 / institutional checklist)
- Iterate through document chunks, accumulating findings across the full corpus
- Identify and flag:
    - Missing required certifications (SOC 2 Type II, ISO 27001, FedRAMP, etc.)
    - Data handling and residency concerns
    - Incident response and breach notification gaps
    - Subprocessor / fourth-party risk disclosures
    - Penetration testing cadence and scope
    - Access control and encryption practices
- Produce a structured FindingsReport with an overall risk score (0–10)
- Save the report in both Markdown and JSON formats to the run folder
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from analysis.document_processor import ProcessedDocument


class RiskLevel(str, Enum):
    """Categorical risk level for an individual finding."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"


@dataclass
class Finding:
    """A single security observation from the document review."""

    title: str
    """Short title of the finding (e.g. 'Missing SOC 2 Type II report')."""

    description: str
    """Detailed description of the issue and why it matters."""

    risk_level: RiskLevel
    """Severity classification."""

    category: str
    """Security domain (e.g. 'Access Control', 'Data Protection', 'Incident Response')."""

    evidence: str
    """Quoted text from the vendor documents that supports this finding."""

    recommendation: str
    """Suggested remediation or follow-up action."""


@dataclass
class FindingsReport:
    """Complete security review report for a single vendor."""

    vendor_name: str
    """Name of the vendor reviewed."""

    risk_score: float
    """Overall risk score from 0.0 (lowest) to 10.0 (highest)."""

    executive_summary: str
    """Two-to-four sentence summary for non-technical stakeholders."""

    findings: list[Finding] = field(default_factory=list)
    """All individual findings, ordered by risk level (critical first)."""

    documents_reviewed: list[str] = field(default_factory=list)
    """Names of the source documents that were analyzed."""

    review_date: str = ""
    """ISO 8601 date string when the review was performed."""


class SecurityReviewer:
    """
    Orchestrates multi-document security analysis using Claude.

    Usage::

        reviewer = SecurityReviewer(run_folder=Path("runs/acme-20240315"))
        report = reviewer.review(vendor_name="Acme Corp", documents=processed_docs)
    """

    def __init__(self, run_folder: Path) -> None:
        """
        Args:
            run_folder: Run folder where the generated report will be saved.
        """
        pass

    def review(self, vendor_name: str, documents: list[ProcessedDocument]) -> FindingsReport:
        """
        Perform a full security review across all provided documents.

        For each document chunk, Claude is prompted to identify security findings.
        Results are consolidated, deduplicated, and scored to produce the final report.

        Args:
            vendor_name: Human-readable vendor name (included in the report header).
            documents:   List of processed documents to analyze.

        Returns:
            A FindingsReport with all findings and an overall risk score.
        """
        pass

    def _analyze_chunk(self, chunk: str, vendor_name: str, doc_name: str) -> list[Finding]:
        """
        Send a single document chunk to Claude and parse the returned findings.

        Args:
            chunk:       A text segment from a processed document.
            vendor_name: Vendor name for prompt context.
            doc_name:    Source document name for attribution.

        Returns:
            List of Finding objects extracted from Claude's response.
        """
        pass

    def _consolidate_findings(self, all_findings: list[Finding]) -> list[Finding]:
        """
        Merge duplicate findings and sort by risk level.

        Args:
            all_findings: Raw findings accumulated across all document chunks.

        Returns:
            Deduplicated, sorted list of findings (critical first).
        """
        pass

    def _calculate_risk_score(self, findings: list[Finding]) -> float:
        """
        Compute a numeric risk score (0.0–10.0) based on the findings.

        Weighting:
        - Critical: 3.0 points each (capped)
        - High:     1.5 points each
        - Medium:   0.5 points each
        - Low:      0.1 points each

        Args:
            findings: Consolidated list of findings.

        Returns:
            Float risk score in the range [0.0, 10.0].
        """
        pass

    def _save_report(self, report: FindingsReport) -> tuple[Path, Path]:
        """
        Serialize the report to Markdown and JSON files in the run folder.

        Args:
            report: The completed FindingsReport.

        Returns:
            Tuple of (markdown_path, json_path).
        """
        pass
