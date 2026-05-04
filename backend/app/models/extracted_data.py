"""Extracted data database model."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class ExtractedData(Base):
    """Stores NLP-extracted information from a court judgment."""

    __tablename__ = "extracted_data"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, unique=True)

    # Extracted fields (now strictly JSON: {value, source_text, page_number, confidence})
    case_title = Column(JSON, default=dict)
    case_number = Column(JSON, default=dict)
    parties_involved = Column(JSON, default=list)  # list of {value: {name, role}, source_text, page_number, confidence}
    date_of_order = Column(JSON, default=dict)
    judge_name = Column(JSON, default=dict)
    court_name = Column(JSON, default=dict)
    key_directives = Column(JSON, default=list)  # list of {value: directive, source_text, page_number, confidence}
    deadlines = Column(JSON, default=list)  # list of {value: {description, date}, source_text, page_number, confidence}
    responsible_authority = Column(JSON, default=dict)

    # Full text
    raw_text = Column(Text, default="")
    page_texts = Column(JSON, default=list)  # [{page_num, text}]

    # Validation and Explainability
    validation_flags = Column(JSON, default=list) # [{rule, message, severity}]
    
    # Kept for backward compatibility if needed, but confidence is now per-field
    extraction_metadata = Column(JSON, default=dict)
    confidence_scores = Column(JSON, default=dict)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    document = relationship("Document", back_populates="extracted_data")
