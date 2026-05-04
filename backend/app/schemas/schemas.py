"""Pydantic schemas for API request/response validation."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ── Document Schemas ──────────────────────────────────────────────

class DocumentResponse(BaseModel):
    """Response schema for a document."""
    id: str
    filename: str
    original_filename: str
    file_size: int
    page_count: int
    status: str
    upload_date: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """Response schema for document list."""
    documents: list[DocumentResponse]
    total: int


# ── Extraction Field Schemas ────────────────────────────────────────

class ExtractedField(BaseModel):
    value: str | dict | None = None
    source_text: str = ""
    page_number: int = 0
    confidence: float = 0.0

class ExtractedPartyField(ExtractedField):
    value: dict = Field(default_factory=dict) # {name, role}

class ExtractedDirectiveField(ExtractedField):
    value: str = "" # directive

class ExtractedDeadlineField(ExtractedField):
    value: dict = Field(default_factory=dict) # {description, date}

class ExtractedDataResponse(BaseModel):
    """Response schema for extracted data."""
    id: str
    document_id: str
    case_title: ExtractedField
    case_number: ExtractedField
    parties_involved: list[ExtractedPartyField]
    date_of_order: ExtractedField
    judge_name: ExtractedField
    court_name: ExtractedField
    key_directives: list[ExtractedDirectiveField]
    deadlines: list[ExtractedDeadlineField]
    responsible_authority: ExtractedField
    
    validation_flags: list[dict]
    
    # Legacy fields
    extraction_metadata: dict
    confidence_scores: dict
    created_at: datetime

    class Config:
        from_attributes = True


# ── Action Plan Schemas ───────────────────────────────────────────

class ActionPlanResponse(BaseModel):
    """Response schema for an action plan."""
    id: str
    document_id: str
    action_required: str
    reasoning: str
    deadline: str
    deadline_date: Optional[datetime] = None
    responsible_department: str
    priority: str
    confidence_score: float
    risk_score: float
    source_text: str
    page_number: Optional[int] = None
    auto_deadlines: list[dict]
    created_at: datetime

    class Config:
        from_attributes = True


class ActionPlanListResponse(BaseModel):
    """Response for multiple action plans."""
    action_plans: list[ActionPlanResponse]


# ── Verification Schemas ─────────────────────────────────────────

class VerificationRequest(BaseModel):
    """Request schema for submitting verification."""
    status: str = Field(..., description="approved, rejected, or edited")
    edits: dict = Field(default_factory=dict, description="Field corrections")
    notes: str = ""
    verified_by: str = "admin"


class VerificationResponse(BaseModel):
    """Response schema for verification."""
    id: str
    document_id: str
    status: str
    verified_by: str
    edits: dict
    notes: str
    verified_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── Dashboard Schemas ─────────────────────────────────────────────

class DashboardSummary(BaseModel):
    """Dashboard summary statistics."""
    total_documents: int = 0
    pending_verification: int = 0
    verified: int = 0
    rejected: int = 0
    high_priority: int = 0
    medium_priority: int = 0
    low_priority: int = 0
    departments: list[dict] = []


class DashboardCase(BaseModel):
    """A verified case for the dashboard."""
    document_id: str
    case_title: str
    case_number: str
    date_of_order: str
    action_required: str
    priority: str
    deadline: str
    deadline_date: Optional[datetime] = None
    responsible_department: str
    confidence_score: float
    risk_score: float
    verified_at: Optional[datetime] = None
    status: str


class DashboardCasesResponse(BaseModel):
    """Response for dashboard cases."""
    cases: list[DashboardCase]
    total: int


class UpcomingDeadline(BaseModel):
    """An upcoming deadline."""
    document_id: str
    case_title: str
    action_required: str
    deadline: str
    deadline_date: Optional[datetime] = None
    responsible_department: str
    priority: str
    days_remaining: Optional[int] = None
