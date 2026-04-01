"""
scraper/tos_checker.py

Reads and interprets a vendor's Terms of Service page to determine whether
automated data collection is explicitly prohibited.

Responsibilities:
- Locate the Terms of Service / Terms of Use page (via common URL patterns
  or by following links on the vendor's homepage)
- Fetch and extract the text content of the ToS page
- Send the text to Claude for a structured analysis:
    - Does the ToS prohibit automated scraping or crawling?
    - Are there data-use restrictions relevant to security reviews?
    - Is there a specific contact required before collecting data?
- Return a structured verdict the orchestrator can act on
- Save the raw ToS text and Claude's analysis to the run folder
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TosVerdict(str, Enum):
    """Possible outcomes of a Terms of Service review."""

    PERMITTED = "permitted"
    """Automated collection appears to be permitted or not addressed."""

    PROHIBITED = "prohibited"
    """ToS explicitly prohibits automated scraping or data collection."""

    UNCLEAR = "unclear"
    """ToS language is ambiguous; human review recommended."""

    NOT_FOUND = "not_found"
    """No Terms of Service page could be located."""


@dataclass
class TosCheckResult:
    """Result of a Terms of Service compliance check."""

    url: str
    """The vendor URL that was checked."""

    verdict: TosVerdict
    """The overall verdict from Claude's analysis."""

    tos_url: str | None
    """The URL of the ToS page that was found and analyzed."""

    reasoning: str
    """Claude's explanation for the verdict."""

    relevant_clauses: list[str]
    """Specific clauses from the ToS that informed the verdict."""

    raw_tos_text: str
    """Full text content of the ToS page (truncated if very long)."""


class TosChecker:
    """
    Locates and analyzes a vendor's Terms of Service using Claude.

    Usage::

        checker = TosChecker()
        result = checker.check("https://acme.example.com")
        if result.verdict == TosVerdict.PROHIBITED:
            raise RuntimeError("Scraping prohibited by ToS")
    """

    # Common URL patterns where Terms of Service pages are found.
    COMMON_TOS_PATHS: tuple[str, ...] = (
        "/terms",
        "/terms-of-service",
        "/terms-of-use",
        "/tos",
        "/legal/terms",
        "/legal",
    )

    def __init__(self) -> None:
        """Initialize the ToS checker with a Claude client."""
        pass

    def check(self, base_url: str) -> TosCheckResult:
        """
        Locate and analyze the Terms of Service for the given vendor URL.

        Args:
            base_url: The vendor's homepage or any URL on their domain.

        Returns:
            A TosCheckResult with a verdict and supporting evidence.
        """
        pass

    def _find_tos_url(self, base_url: str) -> str | None:
        """
        Attempt to locate the ToS page by probing common URL patterns and
        by parsing links on the vendor's homepage.

        Args:
            base_url: The vendor's homepage URL.

        Returns:
            The URL of the ToS page if found, or None.
        """
        pass

    def _fetch_tos_text(self, tos_url: str) -> str:
        """
        Fetch and extract plain text from the ToS page.

        Args:
            tos_url: Direct URL to the Terms of Service page.

        Returns:
            Plain text content of the ToS page.
        """
        pass

    def _analyze_with_claude(self, tos_text: str, vendor_url: str) -> TosCheckResult:
        """
        Send the ToS text to Claude and parse a structured verdict.

        Args:
            tos_text:   Plain text content of the ToS.
            vendor_url: The vendor's base URL (for context in the prompt).

        Returns:
            A TosCheckResult populated from Claude's response.
        """
        pass
