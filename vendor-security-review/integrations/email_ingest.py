"""
integrations/email_ingest.py

Email-based document ingestion for the vendor security review platform.

Responsibilities:
- Connect to the configured email inbox (EMAIL_INGEST_ADDRESS) via IMAP
- Poll for new unread messages at a configurable interval
- Parse email metadata: sender, subject, date, body
- Download and save email attachments to the run folder's raw_docs/ directory
- Extract any document URLs mentioned in the email body for download
- Trigger a new review run via the Orchestrator when documents are received
- Mark processed emails as read (or move to a processed folder)
- Handle multipart MIME messages, inline images, and various encodings

Expected email workflow:
    1. Staff sends a vendor a doc-request email using the template in
       templates/vendor_doc_request.md
    2. Vendor replies to EMAIL_INGEST_ADDRESS with documents attached
    3. EmailIngestor detects the new email and triggers a review run
    4. The originating TDX ticket ID (if included in the subject) is used
       to post results back to the correct ticket
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class IngestedEmail:
    """Represents a single email received at the ingest address."""

    message_id: str
    """Unique IMAP message ID."""

    sender: str
    """From address of the email."""

    subject: str
    """Email subject line."""

    body_text: str
    """Plain text body of the email."""

    attachment_paths: list[Path] = field(default_factory=list)
    """Paths where email attachments were saved."""

    tdx_ticket_id: str | None = None
    """TDX ticket ID parsed from the subject line (e.g. '[TDX-12345]')."""

    vendor_name: str | None = None
    """Vendor name inferred from the email subject or sender domain."""


class EmailIngestor:
    """
    Monitors an IMAP inbox and ingests vendor document submissions.

    Usage::

        ingestor = EmailIngestor(run_folder=Path("runs/acme-20240315"))
        emails = ingestor.fetch_new_emails()
        for email in emails:
            orchestrator.run_from_email(email)
    """

    SUBJECT_TICKET_PATTERN: str = r"\[TDX-(\d+)\]"
    """Regex pattern to extract a TDX ticket ID from an email subject."""

    def __init__(self, runs_root: Path | None = None) -> None:
        """
        Args:
            runs_root: Root directory where run folders are created.
                       Defaults to settings.RUNS_DIR.
        """
        pass

    def fetch_new_emails(self) -> list[IngestedEmail]:
        """
        Connect to the IMAP inbox and retrieve all unread messages.

        Returns:
            List of IngestedEmail objects for each unread message found.
        """
        pass

    def start_polling(self, interval_seconds: int = 60) -> None:
        """
        Begin a blocking poll loop that checks for new emails on an interval.

        Intended for use in a background thread or async task.

        Args:
            interval_seconds: How often to check the inbox (default: 60s).
        """
        pass

    def _download_attachments(self, message, save_dir: Path) -> list[Path]:
        """
        Extract and save all attachments from an email message object.

        Args:
            message:  A parsed email.message.Message object.
            save_dir: Directory where attachments should be saved.

        Returns:
            List of paths to saved attachment files.
        """
        pass

    def _parse_tdx_ticket_id(self, subject: str) -> str | None:
        """
        Extract a TDX ticket ID from an email subject line.

        Looks for patterns like "[TDX-12345]" or "TDX #12345" in the subject.

        Args:
            subject: The raw email subject string.

        Returns:
            The ticket ID string if found, or None.
        """
        pass

    def _mark_as_processed(self, message_id: str) -> None:
        """
        Mark an email as read and optionally move it to a processed folder.

        Args:
            message_id: The IMAP message UID to mark as processed.
        """
        pass
