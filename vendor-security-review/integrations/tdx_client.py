"""
integrations/tdx_client.py

TeamDynamix (TDX) REST API client.

Responsibilities:
- Authenticate against the TDX REST API using a bearer token
- Retrieve ticket details by ticket ID
- Post comments/updates to an existing ticket
- Attach files (e.g., the findings report PDF) to a ticket
- Create new tickets for vendor reviews initiated outside of TDX
- Map vendor review findings to TDX custom field values
- Handle TDX API pagination and rate limiting gracefully

Authentication:
    TDX uses a username/password login to obtain a short-lived bearer token.
    This client manages token acquisition and refresh automatically.

Relevant TDX API endpoints (relative to TDX_BASE_URL):
    POST /api/auth/login             — obtain bearer token
    GET  /api/{app_id}/tickets/{id}  — fetch ticket details
    POST /api/{app_id}/tickets/{id}/comments — post a comment
    POST /api/{app_id}/tickets/{id}/attachments — attach a file
    POST /api/{app_id}/tickets       — create a new ticket
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class TdxTicket:
    """Lightweight representation of a TDX ticket."""

    ticket_id: str
    """Unique identifier for the ticket."""

    title: str
    """Ticket title / subject."""

    status: str
    """Current ticket status (e.g. 'New', 'In Process', 'Resolved')."""

    requestor_name: str
    """Name of the person who submitted the ticket."""

    requestor_email: str
    """Email address of the ticket requestor."""

    custom_fields: dict[str, Any]
    """Map of custom field names to their values."""


class TdxClient:
    """
    Client for interacting with the TeamDynamix REST API.

    Usage::

        client = TdxClient()
        ticket = client.get_ticket("123456")
        client.post_comment("123456", "Security review complete. See attachment.")
        client.attach_file("123456", Path("runs/acme/reports/findings.md"))
    """

    def __init__(self, base_url: str | None = None, api_key: str | None = None) -> None:
        """
        Args:
            base_url: TDX instance base URL. Defaults to settings.TDX_BASE_URL.
            api_key:  TDX API key. Defaults to settings.TDX_API_KEY.
        """
        pass

    def get_ticket(self, ticket_id: str) -> TdxTicket:
        """
        Fetch details for a single TDX ticket.

        Args:
            ticket_id: The TDX ticket identifier.

        Returns:
            A TdxTicket populated with the ticket's current state.

        Raises:
            requests.HTTPError: On non-2xx responses from the TDX API.
        """
        pass

    def post_comment(self, ticket_id: str, body: str, is_private: bool = False) -> None:
        """
        Post a comment to an existing TDX ticket.

        Args:
            ticket_id:  The TDX ticket to comment on.
            body:       Markdown-formatted comment body.
            is_private: If True, the comment is visible only to technicians.
        """
        pass

    def attach_file(self, ticket_id: str, file_path: Path) -> None:
        """
        Upload a file and attach it to a TDX ticket.

        Args:
            ticket_id: The TDX ticket to attach the file to.
            file_path: Local path to the file to upload.

        Raises:
            FileNotFoundError: If file_path does not exist.
        """
        pass

    def create_ticket(
        self,
        title: str,
        description: str,
        requestor_email: str,
        custom_fields: dict[str, Any] | None = None,
    ) -> TdxTicket:
        """
        Create a new TDX ticket for a vendor security review.

        Args:
            title:           Short ticket title.
            description:     Full ticket description (Markdown).
            requestor_email: Email of the person requesting the review.
            custom_fields:   Optional map of custom field names to values.

        Returns:
            The newly created TdxTicket.
        """
        pass

    def _get_headers(self) -> dict[str, str]:
        """
        Build the HTTP headers required for authenticated TDX API requests.

        Returns:
            Dict containing Authorization and Content-Type headers.
        """
        pass
