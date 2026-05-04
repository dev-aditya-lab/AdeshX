"""Extraction API endpoints — trigger and retrieve NLP extraction."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.document import Document, DocumentStatus
from app.models.extracted_data import ExtractedData
from app.models.segment import Segment, SegmentType
from app.schemas.schemas import ExtractedDataResponse
from app.services.ocr_service import extract_text_from_pdf
from app.services.nlp_service import extract_information
from app.services.segmentation_service import segment_document
from app.services.validation_service import validate_extraction

router = APIRouter(prefix="/api/extraction", tags=["Extraction"])


@router.post("/{document_id}/extract", response_model=ExtractedDataResponse)
def trigger_extraction(document_id: str, db: Session = Depends(get_db)):
    """Trigger text extraction, segmentation, and NLP analysis for a document."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Update status
    doc.status = DocumentStatus.PROCESSING.value
    db.commit()

    try:
        # Step 1: Extract text from PDF (OCR)
        ocr_result = extract_text_from_pdf(doc.file_path)
        full_text = ocr_result["full_text"]
        pages = ocr_result["pages"]

        # Step 2: Segmentation
        segments_dict = segment_document(full_text, pages)
        
        # Save segments
        db.query(Segment).filter(Segment.document_id == document_id).delete()
        for s_type, text in segments_dict.items():
            if text:
                db.add(Segment(document_id=document_id, segment_type=s_type, text=text))

        # Step 3: NLP Extraction (Regex + Multi-Pass LLM)
        extracted = extract_information(full_text, pages, segments_dict)
        
        # Step 4: Rule-based Validation
        validation_flags = validate_extraction(extracted)

        # Remove existing extraction if re-running
        existing = db.query(ExtractedData).filter(ExtractedData.document_id == document_id).first()
        if existing:
            db.delete(existing)
            db.flush()

        # Save extracted data
        data = ExtractedData(
            document_id=document_id,
            case_title=extracted.get("case_title", {}),
            case_number=extracted.get("case_number", {}),
            parties_involved=extracted.get("parties_involved", []),
            date_of_order=extracted.get("date_of_order", {}),
            judge_name=extracted.get("judge_name", {}),
            court_name=extracted.get("court_name", {}),
            key_directives=extracted.get("key_directives", []),
            deadlines=extracted.get("deadlines", []),
            responsible_authority=extracted.get("responsible_authority", {}),
            raw_text=full_text,
            page_texts=pages,
            validation_flags=validation_flags,
            extraction_metadata={}, # Legacy
            confidence_scores={},   # Legacy
        )
        db.add(data)

        # Update document status
        doc.status = DocumentStatus.EXTRACTED.value
        doc.page_count = ocr_result["page_count"]
        db.commit()
        db.refresh(data)
        return data

    except Exception as e:
        doc.status = DocumentStatus.UPLOADED.value
        db.commit()
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


@router.get("/{document_id}", response_model=ExtractedDataResponse)
def get_extraction(document_id: str, db: Session = Depends(get_db)):
    """Get extracted data for a document."""
    data = db.query(ExtractedData).filter(ExtractedData.document_id == document_id).first()
    if not data:
        raise HTTPException(status_code=404, detail="No extraction data found for this document")
    return data
