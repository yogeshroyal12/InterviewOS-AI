from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.db.database import get_db
from app.models.document import Document
from app.models.user import User
from app.schemas.document import DocumentResponse
from app.services.document_extractor import DocumentError, extract_text

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])
ALLOWED_TYPES = {"resume", "job_description"}


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def upload_document(
    document_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentResponse:
    if document_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="document_type must be 'resume' or 'job_description'")
    try:
        text = extract_text(file.filename or "", file.file.read())
    except DocumentError as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)) from error

    document = Document(
        user_id=current_user.id,
        document_type=document_type,
        original_filename=(file.filename or "upload")[:255],
        extracted_text=text,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return DocumentResponse(
        id=document.id,
        document_type=document.document_type,
        original_filename=document.original_filename,
        created_at=document.created_at,
        text_preview=text[:200],
    )