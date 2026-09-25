import os
from typing import Tuple
from app.core.exceptions import ValidationException

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "text/markdown",
    "application/octet-stream", # for .md files uploaded via forms
}
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB limit


def validate_document_file(filename: str, content_type: str, file_size: int) -> Tuple[str, str]:
    """Validates document file extension, MIME type, and size limit."""
    ext = os.path.splitext(filename)[1].lower()
    if not ext or ext not in ALLOWED_EXTENSIONS:
        raise ValidationException(
            f"Unsupported file extension '{ext}'. Allowed extensions: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    if file_size > MAX_FILE_SIZE:
        max_mb = MAX_FILE_SIZE // (1024 * 1024)
        raise ValidationException(f"File size exceeds the maximum limit of {max_mb}MB")

    return ext, content_type
