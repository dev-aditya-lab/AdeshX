"""Verification database model."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class VerificationStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EDITED = "edited"


class Verification(Base):
    """Human-in-the-loop verification record."""

    __tablename__ = "verifications"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, unique=True)

    status = Column(String(20), default=VerificationStatus.PENDING.value)
    verified_by = Column(String(200), default="admin")

    # User edits (stores corrections made during verification)
    edits = Column(JSON, default=dict)
    # {field_name: {original: ..., corrected: ...}}

    notes = Column(Text, default="")
    verified_at = Column(DateTime, nullable=True)

    # Relationships
    document = relationship("Document", back_populates="verification")
