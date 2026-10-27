from io import BytesIO

import pytest
from docx import Document

from app.services.document_extractor import DocumentError, extract_text


def make_docx(*lines: str) -> bytes:
    document = Document()
    for line in lines:
        document.add_paragraph(line)
    buffer = BytesIO()
    document.save(buffer)
    return buffer.getvalue()


def test_extracts_docx_text() -> None:
    data = make_docx("Python developer", "FastAPI experience")
    assert extract_text("resume.docx", data) == "Python developer\nFastAPI experience"


def test_rejects_empty_file() -> None:
    with pytest.raises(DocumentError):
        extract_text("resume.docx", b"")


def test_rejects_fake_pdf() -> None:
    with pytest.raises(DocumentError):
        extract_text("resume.pdf", b"this is not really a pdf")