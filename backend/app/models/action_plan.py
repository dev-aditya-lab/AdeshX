"""Action plan database model."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class ActionType(str, enum.Enum):
    COMPLIANCE = "compliance"
    APPEAL = "appeal"
    REVIEW = "review"
    IMPLEMENTATION = "implementation"


class Priority(str, enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ActionPlan(Base):
    """Generated action plan for government officials."""

    __tablename__ = "action_plans"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    extracted_data_id = Column(String, ForeignKey("extracted_data.id", ondelete="CASCADE"), nullable=True)

    # Action details
    action_required = Column(String(50), default=ActionType.REVIEW.value)
    reasoning = Column(Text, default="")
    deadline = Column(String(100), default="")
    deadline_date = Column(DateTime, nullable=True)
    responsible_department = Column(String(500), default="")
    priority = Column(String(20), default=Priority.MEDIUM.value)

    # Scores
    confidence_score = Column(Float, default=0.0)
    risk_score = Column(Float, default=0.0)

    # Explainability
    source_text = Column(Text, default="")
    page_number = Column(Integer, nullable=True)

    # Auto-calculated deadlines
    auto_deadlines = Column(JSON, default=list)
    # [{type: "appeal", days: 30, calculated_date, source}]

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    document = relationship("Document", back_populates="action_plans")
