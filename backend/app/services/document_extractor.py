from io import BytesIO

from docx import Document
from pypdf import PdfReader

MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # 5 MB limit
PDF_SIGNATURE = b"%PDF"
DOCX_SIGNATURE = b"PK"  # DOCX files are ZIP archives


class DocumentError(ValueError):
    """Raised when an uploaded file cannot be used."""


def extract_text(filename: str, data: bytes) -> str:
    """Return the plain text of a PDF or DOCX file, or raise DocumentError."""
    if not data:
        raise DocumentError("The file is empty.")
    if len(data) > MAX_UPLOAD_BYTES:
        raise DocumentError("The file is larger than 5 MB.")

    name = filename.lower()
    if name.endswith(".pdf") and data.startswith(PDF_SIGNATURE):
        reader = PdfReader(BytesIO(data))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    elif name.endswith(".docx") and data.startswith(DOCX_SIGNATURE):
        document = Document(BytesIO(data))
        text = "\n".join(paragraph.text for paragraph in document.paragraphs)
    else:
        raise DocumentError("Only valid PDF or DOCX files are supported.")

    text = text.strip()
    if not text:
        raise DocumentError("No readable text was found in the file.")
    return text