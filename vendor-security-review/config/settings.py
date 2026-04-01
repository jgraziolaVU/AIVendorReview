"""
config/settings.py

Centralized configuration module for the vendor-security-review project.

Loads environment variables from a .env file and exposes them as typed
constants consumed by all other modules. Also defines application-level
defaults (e.g., output directory, supported file extensions).
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Load .env
# ---------------------------------------------------------------------------

load_dotenv()


# ---------------------------------------------------------------------------
# Anthropic / Claude
# ---------------------------------------------------------------------------

ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
"""API key used to authenticate with the Anthropic API."""

CLAUDE_MODEL: str = "claude-opus-4-6"
"""Default Claude model used for all AI-powered steps."""


# ---------------------------------------------------------------------------
# TeamDynamix
# ---------------------------------------------------------------------------

TDX_BASE_URL: str = os.getenv("TDX_BASE_URL", "")
"""Base URL for the institution's TeamDynamix instance (no trailing slash)."""

TDX_API_KEY: str = os.getenv("TDX_API_KEY", "")
"""API key for authenticating against the TeamDynamix REST API."""


# ---------------------------------------------------------------------------
# Email ingestion
# ---------------------------------------------------------------------------

EMAIL_INGEST_ADDRESS: str = os.getenv("EMAIL_INGEST_ADDRESS", "")
"""Email address monitored for incoming vendor security documents."""


# ---------------------------------------------------------------------------
# Folder watcher
# ---------------------------------------------------------------------------

WATCHED_FOLDER_PATH: Path = Path(os.getenv("WATCHED_FOLDER_PATH", "./watched"))
"""Local filesystem path watched by watchdog for dropped documents."""


# ---------------------------------------------------------------------------
# Run output
# ---------------------------------------------------------------------------

RUNS_DIR: Path = Path(__file__).resolve().parent.parent / "runs"
"""Root directory where per-vendor review run folders are created."""

SUPPORTED_DOCUMENT_EXTENSIONS: tuple[str, ...] = (".pdf", ".docx", ".doc", ".txt", ".md")
"""File extensions treated as reviewable documents during ingestion."""
