"""Dashboard API endpoints — stats, verified cases, deadlines."""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.document import Document, DocumentStatus
from app.models.extracted_data import ExtractedData
from app.models.action_plan import ActionPlan
from app.models.verification import Verification, VerificationStatus
from app.schemas.schemas import DashboardSummary, DashboardCasesResponse, DashboardCase, UpcomingDeadline

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_summary(db: Session = Depends(get_db)):
    """Get dashboard summary statistics."""
    total = db.query(Document).count()
    pending = db.query(Verification).filter(Verification.status == VerificationStatus.PENDING.value).count()
    verified = db.query(Document).filter(Document.status == DocumentStatus.VERIFIED.value).count()
    rejected = db.query(Document).filter(Document.status == DocumentStatus.REJECTED.value).count()

    # Priority counts (from verified cases only)
    high = db.query(ActionPlan).join(Document).filter(
        Document.status == DocumentStatus.VERIFIED.value,
        ActionPlan.priority == "high"
    ).count()
    medium = db.query(ActionPlan).join(Document).filter(
        Document.status == DocumentStatus.VERIFIED.value,
        ActionPlan.priority == "medium"
    ).count()
    low = db.query(ActionPlan).join(Document).filter(
        Document.status == DocumentStatus.VERIFIED.value,
        ActionPlan.priority == "low"
    ).count()

    # Department breakdown
    dept_counts = (
        db.query(ActionPlan.responsible_department, func.count(ActionPlan.id))
        .join(Document)
        .filter(Document.status == DocumentStatus.VERIFIED.value)
        .group_by(ActionPlan.responsible_department)
        .all()
    )
    departments = [{"department": d[0], "count": d[1]} for d in dept_counts if d[0]]

    return DashboardSummary(
        total_documents=total,
        pending_verification=pending,
        verified=verified,
        rejected=rejected,
        high_priority=high,
        medium_priority=medium,
        low_priority=low,
        departments=departments,
    )


@router.get("/cases", response_model=DashboardCasesResponse)
def get_cases(
    department: str = Query(None),
    priority: str = Query(None),
    action_type: str = Query(None),
    db: Session = Depends(get_db),
):
    """Get verified cases with optional filters."""
    query = (
        db.query(Document, ExtractedData, ActionPlan, Verification)
        .join(ExtractedData, ExtractedData.document_id == Document.id)
        .join(ActionPlan, ActionPlan.document_id == Document.id)
        .outerjoin(Verification, Verification.document_id == Document.id)
        .filter(Document.status == DocumentStatus.VERIFIED.value)
    )

    if department:
        query = query.filter(ActionPlan.responsible_department.ilike(f"%{department}%"))
    if priority:
        query = query.filter(ActionPlan.priority == priority)
    if action_type:
        query = query.filter(ActionPlan.action_required == action_type)

    results = query.all()

    def get_json_val(field, default=""):
        if not field:
            return default
        if isinstance(field, dict):
            return field.get("value", default) or default
        return str(field)

    cases = []
    for doc, ext, plan, ver in results:
        cases.append(DashboardCase(
            document_id=doc.id,
            case_title=get_json_val(ext.case_title, "Unknown Case"),
            case_number=get_json_val(ext.case_number, ""),
            date_of_order=get_json_val(ext.date_of_order, ""),
            action_required=plan.action_required,
            priority=plan.priority,
            deadline=plan.deadline,
            deadline_date=plan.deadline_date,
            responsible_department=plan.responsible_department,
            confidence_score=plan.confidence_score,
            risk_score=plan.risk_score,
            verified_at=ver.verified_at if ver else None,
            status=doc.status,
        ))

    return DashboardCasesResponse(cases=cases, total=len(cases))


@router.get("/deadlines", response_model=list[UpcomingDeadline])
def get_deadlines(db: Session = Depends(get_db)):
    """Get upcoming deadlines sorted by urgency."""
    results = (
        db.query(Document, ExtractedData, ActionPlan)
        .join(ExtractedData, ExtractedData.document_id == Document.id)
        .join(ActionPlan, ActionPlan.document_id == Document.id)
        .filter(Document.status == DocumentStatus.VERIFIED.value)
        .filter(ActionPlan.deadline_date.isnot(None))
        .order_by(ActionPlan.deadline_date.asc())
        .all()
    )

    def get_json_val(field, default=""):
        if not field:
            return default
        if isinstance(field, dict):
            return field.get("value", default) or default
        return str(field)

    deadlines = []
    now = datetime.utcnow()
    for doc, ext, plan in results:
        days_remaining = None
        if plan.deadline_date:
            days_remaining = (plan.deadline_date - now).days

        deadlines.append(UpcomingDeadline(
            document_id=doc.id,
            case_title=get_json_val(ext.case_title, "Unknown Case"),
            action_required=plan.action_required,
            deadline=plan.deadline,
            deadline_date=plan.deadline_date,
            responsible_department=plan.responsible_department,
            priority=plan.priority,
            days_remaining=days_remaining,
        ))

    return deadlines
