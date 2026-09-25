import io
from typing import List, Tuple
from pypdf import PdfReader
from docx import Document as DocxDocument
import structlog
from app.core.exceptions import ValidationException

logger = structlog.get_logger(__name__)


class TextExtractor:
    """Extracts plain text and page metadata from PDF, DOCX, TXT, and Markdown files."""

    @staticmethod
    def extract_pdf(file_bytes: bytes) -> Tuple[List[Tuple[int, str]], int]:
        """Extracts text page-by-page from a PDF file."""
        pages = []
        reader = PdfReader(io.BytesIO(file_bytes))
        total_pages = len(reader.pages)

        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if text.strip():
                pages.append((i + 1, text.strip()))

        return pages, total_pages

    @staticmethod
    def extract_docx(file_bytes: bytes) -> Tuple[List[Tuple[int, str]], int]:
        """Extracts text from a DOCX file."""
        doc = DocxDocument(io.BytesIO(file_bytes))
        full_text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        return [(1, full_text)], 1

    @staticmethod
    def extract_plain_text(file_bytes: bytes) -> Tuple[List[Tuple[int, str]], int]:
        """Extracts text from TXT or Markdown files."""
        try:
            text = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            text = file_bytes.decode("latin-1", errors="ignore")
        return [(1, text.strip())], 1

    @classmethod
    def extract_text(cls, file_bytes: bytes, extension: str) -> Tuple[List[Tuple[int, str]], int]:
        ext = extension.lower()
        if ext == ".pdf":
            return cls.extract_pdf(file_bytes)
        elif ext == ".docx":
            return cls.extract_docx(file_bytes)
        elif ext in {".txt", ".md"}:
            return cls.extract_plain_text(file_bytes)
        else:
            raise ValidationException(f"Unsupported file format for extraction: {extension}")
