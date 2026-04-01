"""
analysis/document_processor.py

Ingests vendor security documents (PDFs, DOCX, plain text, Markdown) and
converts them to normalized plain text suitable for Claude analysis.

Responsibilities:
- Detect document type by file extension and/or MIME type
- Extract text from PDFs using pdfplumber (preserving page structure)
- Extract text from DOCX files using python-docx
- Handle plain text and Markdown files directly
- Chunk large documents into segments that fit within Claude's context window
- Save normalized text to the run folder's processed/ sub-directory
- Return structured document objects with metadata (page count, word count, etc.)

Supported formats:
- PDF  (.pdf)  — via pdfplumber
- DOCX (.docx) — via python-docx
- DOC  (.doc)  — best-effort via python-docx (limited support)
- TXT  (.txt)  — direct read
- MD   (.md)   — direct read
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ProcessedDocument:
    """Normalized representation of a single vendor document."""

    source_path: Path
    """Original file path."""

    document_type: str
    """Detected file type (e.g. 'pdf', 'docx', 'txt')."""

    full_text: str
    """Complete extracted plain text."""

    chunks: list[str] = field(default_factory=list)
    """Text split into context-window-sized chunks for Claude."""

    page_count: int = 0
    """Number of pages (for PDFs) or sections (for DOCX)."""

    word_count: int = 0
    """Approximate word count of the extracted text."""

    metadata: dict = field(default_factory=dict)
    """Additional metadata extracted from the document (author, date, title, etc.)."""


class DocumentProcessor:
    """
    Converts raw vendor documents into normalized text for AI analysis.

    Usage::

        processor = DocumentProcessor(run_folder=Path("runs/acme-20240315"))
        docs = processor.process_all([Path("soc2_report.pdf"), Path("sig_questionnaire.docx")])
    """

    DEFAULT_CHUNK_SIZE: int = 50_000
    """Maximum characters per chunk when splitting large documents."""

    DEFAULT_CHUNK_OVERLAP: int = 500
    """Number of characters of overlap between consecutive chunks."""

    def __init__(self, run_folder: Path, chunk_size: int = DEFAULT_CHUNK_SIZE) -> None:
        """
        Args:
            run_folder:  The run folder where processed text files will be saved.
            chunk_size:  Maximum characters per chunk.
        """
        pass

    def process(self, document_path: Path) -> ProcessedDocument:
        """
        Extract and normalize text from a single document file.

        Args:
            document_path: Path to the source document.

        Returns:
            A ProcessedDocument with extracted text and metadata.

        Raises:
            ValueError: If the file extension is not supported.
            FileNotFoundError: If the file does not exist.
        """
        pass

    def process_all(self, document_paths: list[Path]) -> list[ProcessedDocument]:
        """
        Process a list of documents, returning results for all files.

        Files that fail to process are logged but do not halt processing of
        the remaining documents.

        Args:
            document_paths: List of paths to source documents.

        Returns:
            List of ProcessedDocument objects (one per successfully processed file).
        """
        pass

    def _extract_pdf(self, path: Path) -> tuple[str, int, dict]:
        """
        Extract text from a PDF using pdfplumber.

        Args:
            path: Path to the PDF file.

        Returns:
            Tuple of (full_text, page_count, metadata_dict).
        """
        pass

    def _extract_docx(self, path: Path) -> tuple[str, int, dict]:
        """
        Extract text from a DOCX file using python-docx.

        Args:
            path: Path to the DOCX file.

        Returns:
            Tuple of (full_text, section_count, metadata_dict).
        """
        pass

    def _chunk_text(self, text: str) -> list[str]:
        """
        Split a long text string into overlapping chunks.

        Args:
            text: The full text to chunk.

        Returns:
            List of text chunks, each no longer than self.chunk_size characters.
        """
        pass

    def _save_processed(self, doc: ProcessedDocument) -> Path:
        """
        Save the extracted plain text to the run folder's processed/ directory.

        Args:
            doc: The ProcessedDocument to persist.

        Returns:
            Path to the saved text file.
        """
        pass
