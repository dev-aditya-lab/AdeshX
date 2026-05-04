"""Document API endpoints — upload, list, get, serve PDF."""

import os
import uuid
import shutil
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.document import Document, DocumentStatus
from app.schemas.schemas import DocumentResponse, DocumentListResponse
from app.services.ocr_service import get_page_count
from app.config import settings

router = APIRouter(prefix="/api/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload a PDF document."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    # Generate unique filename
    doc_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1]
    safe_filename = f"{doc_id}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)

    # Save file
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Get file info
    file_size = os.path.getsize(file_path)
    page_count = get_page_count(file_path)

    # Create DB record
    doc = Document(
        id=doc_id,
        filename=safe_filename,
        original_filename=file.filename,
        file_path=file_path,
        file_size=file_size,
        page_count=page_count,
        status=DocumentStatus.UPLOADED.value,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    return doc


@router.get("/", response_model=DocumentListResponse)
def list_documents(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """List all uploaded documents."""
    docs = db.query(Document).order_by(Document.upload_date.desc()).offset(skip).limit(limit).all()
    total = db.query(Document).count()
    return DocumentListResponse(documents=docs, total=total)


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: str, db: Session = Depends(get_db)):
    """Get a single document by ID."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.get("/{document_id}/pdf")
def serve_pdf(document_id: str, db: Session = Depends(get_db)):
    """Serve the PDF file for viewing."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="PDF file not found on disk")
    return FileResponse(
        doc.file_path, 
        media_type="application/pdf", 
        filename=doc.original_filename,
        content_disposition_type="inline"
    )


@router.delete("/{document_id}")
def delete_document(document_id: str, db: Session = Depends(get_db)):
    """Delete a document and its file."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete file
    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)

    db.delete(doc)
    db.commit()
    return {"message": "Document deleted", "id": document_id}
