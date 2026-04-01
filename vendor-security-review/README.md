# Vendor Security Review

An AI-powered vendor security review platform that automates the collection, analysis, and reporting of vendor security documentation using Claude AI.

## Purpose

Higher-education IT departments must evaluate third-party vendors for security and compliance before onboarding them. This process typically involves:

- Manually emailing vendors to request security documentation
- Downloading and reading lengthy PDFs (SOC 2 reports, SIG questionnaires, penetration test summaries, etc.)
- Cross-referencing vendor claims against institutional policies
- Filing tickets in TeamDynamix (TDX) to track review status
- Writing up findings for stakeholders

This project automates the entire workflow — from document ingestion to AI-powered analysis to ticketing — reducing review time from days to minutes.

---

## Architecture

```
vendor-security-review/
├── config/
│   └── settings.py           # Centralized config & env vars
├── core/
│   ├── orchestrator.py       # Main workflow engine (ties all modules together)
│   └── folder_manager.py     # Creates and manages per-run output folders
├── scraper/
│   ├── robots_analyzer.py    # Fetches and parses robots.txt before scraping
│   ├── tos_checker.py        # Reads vendor Terms of Service for scraping permissions
│   └── dynamic_scraper.py    # Claude-generated, dynamically executed scraper logic
├── analysis/
│   ├── document_processor.py # Ingests PDFs, DOCX, and other document types
│   └── security_reviewer.py  # Claude-powered deep security analysis
├── integrations/
│   ├── tdx_client.py         # TeamDynamix REST API client
│   └── email_ingest.py       # Watches an inbox for vendor-submitted documents
├── dashboard/                # (Future) Web UI for managing reviews
├── templates/
│   └── vendor_doc_request.md # Email template to request docs from vendors
├── runs/                     # Output folder; each review run gets a subfolder
└── tests/                    # Unit and integration tests
```

---

## Workflow

```
                        ┌─────────────────────────────────────────┐
                        │             Trigger (one of):           │
                        │  - CLI command with vendor name/URL     │
                        │  - TDX ticket webhook                   │
                        │  - Email received in ingest inbox       │
                        │  - File dropped in watched folder       │
                        └────────────────┬────────────────────────┘
                                         │
                                         ▼
                        ┌─────────────────────────────────────────┐
                        │         core/orchestrator.py            │
                        │  - Creates a run folder (runs/<vendor>) │
                        │  - Coordinates all downstream steps     │
                        └──┬──────────┬──────────────┬────────────┘
                           │          │              │
               ┌───────────▼──┐  ┌────▼─────┐  ┌───▼──────────────┐
               │   Scraper    │  │  Email   │  │  Folder Watcher  │
               │  robots.txt  │  │  Ingest  │  │  (watchdog)      │
               │  ToS check   │  └────┬─────┘  └───┬──────────────┘
               │  Dynamic     │       │             │
               │  scraping    │       └──────┬──────┘
               └───────┬──────┘              │
                       │              ┌──────▼──────────────────────┐
                       │              │  analysis/document_processor │
                       │              │  - PDF, DOCX, text parsing   │
                       └──────────────►  - Chunking & normalization  │
                                      └──────────────┬──────────────┘
                                                     │
                                      ┌──────────────▼──────────────┐
                                      │  analysis/security_reviewer  │
                                      │  - Claude AI analysis        │
                                      │  - Policy gap detection      │
                                      │  - Risk scoring              │
                                      └──────────────┬──────────────┘
                                                     │
                                      ┌──────────────▼──────────────┐
                                      │  integrations/tdx_client     │
                                      │  - Update/create TDX ticket  │
                                      │  - Attach findings report    │
                                      └─────────────────────────────┘
```

### Step-by-step

1. **Trigger** — A review is initiated via CLI, a TDX webhook, an incoming email, or a file dropped into a watched folder.
2. **Run folder created** — `folder_manager` creates `runs/<vendor-name>-<timestamp>/` to store all artifacts for this review.
3. **Scraping** — If a vendor URL is provided, the scraper checks `robots.txt` and the Terms of Service before proceeding. Claude generates a custom scraper to extract the relevant security pages.
4. **Document ingestion** — PDFs, DOCX files, and other documents (submitted by vendor via email or dropped in the watched folder) are parsed and normalized.
5. **AI analysis** — Claude reviews the processed content against a configurable security framework (e.g., NIST CSF, ISO 27001, institutional policy checklist).
6. **Report generation** — A structured findings report is written to the run folder.
7. **TDX integration** — The findings are posted back to the originating TeamDynamix ticket as a comment and/or attachment.

---

## Setup

### 1. Clone and install dependencies

```bash
git clone <repo-url>
cd vendor-security-review
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and fill in your credentials
```

### 3. Run a review

```bash
# (CLI interface to be implemented)
python -m core.orchestrator --vendor "Acme Corp" --url "https://acmecorp.example.com"
```

---

## Environment Variables

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | API key for Claude (Anthropic) |
| `TDX_BASE_URL` | Base URL for your TeamDynamix instance |
| `TDX_API_KEY` | TeamDynamix REST API key |
| `EMAIL_INGEST_ADDRESS` | Email address monitored for vendor documents |
| `WATCHED_FOLDER_PATH` | Local folder path watched for dropped documents |

---

## Security & Compliance Notes

- **robots.txt is always honored** before any web scraping occurs.
- **Terms of Service are reviewed** by Claude before scraping proceeds.
- API keys are never committed to source control — use `.env` (gitignored).
- All run artifacts are stored locally in `runs/` and are gitignored by default.

---

## Future Work

- Web dashboard (FastAPI + Jinja2) for managing and viewing reviews
- Multi-vendor batch processing
- Configurable scoring rubrics per institutional policy framework
- Slack/Teams notification integration
