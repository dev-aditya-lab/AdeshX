"""Document database model."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class DocumentStatus(str, enum.Enum):
    """Document processing status."""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    EXTRACTED = "extracted"
    ACTION_GENERATED = "action_generated"
    VERIFIED = "verified"
    REJECTED = "rejected"


class Document(Base):
    """Represents an uploaded court judgment PDF."""

    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String(500), nullable=False)
    original_filename = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_size = Column(Integer, default=0)
    page_count = Column(Integer, default=0)
    status = Column(String(50), default=DocumentStatus.UPLOADED.value)
    upload_date = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    extracted_data = relationship("ExtractedData", back_populates="document", uselist=False, cascade="all, delete-orphan")
    action_plans = relationship("ActionPlan", back_populates="document", cascade="all, delete-orphan")
    verification = relationship("Verification", back_populates="document", uselist=False, cascade="all, delete-orphan")
    segments = relationship("Segment", back_populates="document", cascade="all, delete-orphan")
