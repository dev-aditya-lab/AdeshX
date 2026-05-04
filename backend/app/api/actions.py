"""Action plan & verification API endpoints."""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.document import Document, DocumentStatus
from app.models.extracted_data import ExtractedData
from app.models.action_plan import ActionPlan
from app.models.verification import Verification, VerificationStatus
from app.schemas.schemas import (
    ActionPlanResponse, ActionPlanListResponse,
    VerificationRequest, VerificationResponse,
)
from app.services.action_engine import generate_action_plan

router = APIRouter(prefix="/api/actions", tags=["Actions"])


@router.post("/{document_id}/generate", response_model=ActionPlanResponse)
def generate_actions(document_id: str, db: Session = Depends(get_db)):
    """Generate action plan for a document."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    extracted = db.query(ExtractedData).filter(ExtractedData.document_id == document_id).first()
    if not extracted:
        raise HTTPException(status_code=400, detail="Extraction must be done first")

    # Get segments
    from app.models.segment import Segment
    segments_db = db.query(Segment).filter(Segment.document_id == document_id).all()
    segments_dict = {s.segment_type: s.text for s in segments_db}

    # Generate action plan
    extracted_dict = {
        "case_title": extracted.case_title,
        "case_number": extracted.case_number,
        "parties_involved": extracted.parties_involved,
        "date_of_order": extracted.date_of_order,
        "judge_name": extracted.judge_name,
        "court_name": extracted.court_name,
        "key_directives": extracted.key_directives,
        "deadlines": extracted.deadlines,
    }
    plan_data = generate_action_plan(extracted_dict, segments_dict)

    # Remove existing plans
    db.query(ActionPlan).filter(ActionPlan.document_id == document_id).delete()
    db.flush()

    # Parse deadline date
    deadline_date = None
    try:
        for fmt in ["%d %B %Y", "%Y-%m-%d", "%d/%m/%Y"]:
            try:
                deadline_date = datetime.strptime(plan_data.get("deadline", ""), fmt)
                break
            except ValueError:
                continue
    except Exception:
        pass

    plan = ActionPlan(
        document_id=document_id,
        extracted_data_id=extracted.id,
        action_required=plan_data.get("action_required", "review"),
        reasoning=plan_data.get("reasoning", ""),
        deadline=plan_data.get("deadline", ""),
        deadline_date=deadline_date,
        responsible_department=plan_data.get("responsible_department", ""),
        priority=plan_data.get("priority", "medium"),
        confidence_score=plan_data.get("confidence_score", 0.0),
        risk_score=plan_data.get("risk_score", 0.0),
        source_text=plan_data.get("source_text", ""),
        auto_deadlines=plan_data.get("auto_deadlines", []),
    )
    db.add(plan)

    # Create verification record (pending)
    existing_v = db.query(Verification).filter(Verification.document_id == document_id).first()
    if not existing_v:
        verification = Verification(document_id=document_id, status=VerificationStatus.PENDING.value)
        db.add(verification)

    doc.status = DocumentStatus.ACTION_GENERATED.value
    db.commit()
    db.refresh(plan)
    return plan


@router.get("/{document_id}", response_model=ActionPlanListResponse)
def get_actions(document_id: str, db: Session = Depends(get_db)):
    """Get action plans for a document."""
    plans = db.query(ActionPlan).filter(ActionPlan.document_id == document_id).all()
    return ActionPlanListResponse(action_plans=plans)


@router.put("/{document_id}/verify", response_model=VerificationResponse)
def verify_action(document_id: str, req: VerificationRequest, db: Session = Depends(get_db)):
    """Submit human verification for a document's action plan."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    verification = db.query(Verification).filter(Verification.document_id == document_id).first()
    if not verification:
        verification = Verification(document_id=document_id)
        db.add(verification)

    verification.status = req.status
    verification.verified_by = req.verified_by
    verification.edits = req.edits
    verification.notes = req.notes
    verification.verified_at = datetime.utcnow()

    # Update document status
    if req.status == "approved":
        doc.status = DocumentStatus.VERIFIED.value
    elif req.status == "rejected":
        doc.status = DocumentStatus.REJECTED.value

    db.commit()
    db.refresh(verification)
    return verification


@router.get("/{document_id}/verification", response_model=VerificationResponse)
def get_verification(document_id: str, db: Session = Depends(get_db)):
    """Get verification status for a document."""
    v = db.query(Verification).filter(Verification.document_id == document_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="No verification record found")
    return v
