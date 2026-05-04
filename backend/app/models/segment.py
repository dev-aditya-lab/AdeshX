"""Document segment database model."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class SegmentType(str, enum.Enum):
    HEADER = "header"
    BODY = "body"
    FINAL_JUDGMENT = "final_judgment"
    UNKNOWN = "unknown"


class Segment(Base):
    """Represents a text segment of a document."""

    __tablename__ = "segments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    
    segment_type = Column(String(50), default=SegmentType.UNKNOWN.value)
    text = Column(Text, nullable=False)
    page_range = Column(JSON, default=list)  # e.g., [1, 2]
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    document = relationship("Document", back_populates="segments")
