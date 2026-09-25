import pytest
from app.utils.file_validation import validate_document_file
from app.core.exceptions import ValidationException


def test_file_extension_validation():
    # Valid files
    ext, mime = validate_document_file("sample.pdf", "application/pdf", 1024)
    assert ext == ".pdf"

    ext, mime = validate_document_file("notes.md", "text/markdown", 500)
    assert ext == ".md"

    # Invalid file extension
    with pytest.raises(ValidationException):
        validate_document_file("malicious.exe", "application/octet-stream", 1024)

    # Oversized file
    with pytest.raises(ValidationException):
        validate_document_file("big.pdf", "application/pdf", 30 * 1024 * 1024)
