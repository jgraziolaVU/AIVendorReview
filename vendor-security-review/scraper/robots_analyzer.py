"""
scraper/robots_analyzer.py

Fetches and parses a vendor's robots.txt to determine whether automated
scraping is permitted before any requests are made to the site.

Responsibilities:
- Download robots.txt from the root of the target domain
- Parse the file using the standard urllib.robotparser library
- Evaluate whether our user-agent is allowed to fetch specific paths
- Return a structured permission summary that the orchestrator uses to
  decide whether to proceed with scraping
- Log all access decisions for the run audit trail
"""

from __future__ import annotations

from dataclasses import dataclass
from urllib.robotparser import RobotFileParser


@dataclass
class RobotsPermission:
    """Represents the scraping permission derived from a site's robots.txt."""

    url: str
    """The base URL whose robots.txt was analyzed."""

    can_scrape: bool
    """True if our user-agent is allowed to fetch the site root."""

    disallowed_paths: list[str]
    """Paths explicitly disallowed for our user-agent."""

    crawl_delay: float | None
    """Crawl-delay directive value in seconds, if present."""

    robots_txt_content: str
    """Raw text content of the fetched robots.txt file."""


class RobotsAnalyzer:
    """
    Checks a vendor's robots.txt and evaluates scraping permissions.

    Usage::

        analyzer = RobotsAnalyzer(user_agent="VendorSecurityReviewBot/1.0")
        permission = analyzer.check("https://acme.example.com")
        if permission.can_scrape:
            ...
    """

    DEFAULT_USER_AGENT: str = "VendorSecurityReviewBot/1.0"

    def __init__(self, user_agent: str = DEFAULT_USER_AGENT) -> None:
        """
        Args:
            user_agent: The user-agent string to evaluate against robots.txt rules.
        """
        pass

    def check(self, base_url: str) -> RobotsPermission:
        """
        Fetch and evaluate robots.txt for the given base URL.

        Args:
            base_url: The homepage or any URL on the target domain.

        Returns:
            A RobotsPermission describing what is and isn't allowed.

        Raises:
            requests.RequestException: If robots.txt cannot be fetched and
                                       strict mode is enabled.
        """
        pass

    def is_path_allowed(self, base_url: str, path: str) -> bool:
        """
        Check whether a specific path on a domain is allowed for scraping.

        Args:
            base_url: The domain to check (scheme + host only).
            path:     The URL path to evaluate (e.g. "/security/compliance").

        Returns:
            True if the path may be fetched, False otherwise.
        """
        pass

    def _fetch_robots_txt(self, robots_url: str) -> str:
        """
        Download the raw robots.txt content from the given URL.

        Args:
            robots_url: Full URL to robots.txt (e.g. "https://acme.example.com/robots.txt").

        Returns:
            Raw text content of the file, or an empty string if not found (404).
        """
        pass
