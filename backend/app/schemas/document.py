from datetime import datetime

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: int
    document_type: str
    original_filename: str
    created_at: datetime
    text_preview: str