"""SQLAlchemy models for MDIA."""

import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import (
    Column, String, Integer, Boolean, Text, DateTime, Date,
    Numeric, ForeignKey, TypeDecorator
)
from sqlalchemy.orm import relationship

from db.database import Base


# UUID type that works with both SQLite and PostgreSQL
class GUID(TypeDecorator):
    """Platform-independent GUID type."""
    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return str(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return uuid.UUID(value)
        return value


class Document(Base):
    """Uploaded document metadata."""
    __tablename__ = "documents"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)
    upload_date = Column(DateTime(timezone=True), default=datetime.utcnow)
    processed = Column(Boolean, default=False)
    processing_status = Column(String(50), default="pending")
    raw_text = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    records = relationship("ExtractedRecord", back_populates="document", cascade="all, delete-orphan")
    anomalies = relationship("Anomaly", back_populates="document", cascade="all, delete-orphan")


class ExtractedRecord(Base):
    """Extracted and normalized maintenance record."""
    __tablename__ = "extracted_records"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    document_id = Column(GUID(), ForeignKey("documents.id", ondelete="CASCADE"))
    component = Column(String(255))
    system = Column(String(255))
    failure_type = Column(String(255))
    maint_action = Column(Text)
    priority = Column(String(50))
    start_date = Column(Date)
    end_date = Column(Date)
    cost_estimate = Column(Numeric(12, 2))
    summary_notes = Column(Text)
    status = Column(String(50), default="open")
    assigned_to = Column(String(255))
    confidence_score = Column(Numeric(3, 2))
    extraction_method = Column(String(50))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    document = relationship("Document", back_populates="records")
    anomalies = relationship("Anomaly", back_populates="record", cascade="all, delete-orphan")
    status_updates = relationship("StatusUpdate", back_populates="record", cascade="all, delete-orphan")


class Anomaly(Base):
    """Detected data quality anomaly."""
    __tablename__ = "anomalies"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    record_id = Column(GUID(), ForeignKey("extracted_records.id", ondelete="CASCADE"))
    document_id = Column(GUID(), ForeignKey("documents.id", ondelete="CASCADE"))
    anomaly_type = Column(String(100), nullable=False)
    severity = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    field_name = Column(String(100))
    field_value = Column(Text)
    suggested_fix = Column(Text)
    resolved = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    record = relationship("ExtractedRecord", back_populates="anomalies")
    document = relationship("Document", back_populates="anomalies")


class StatusUpdate(Base):
    """Status change history."""
    __tablename__ = "status_updates"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    record_id = Column(GUID(), ForeignKey("extracted_records.id", ondelete="CASCADE"))
    previous_status = Column(String(50))
    new_status = Column(String(50), nullable=False)
    assigned_to = Column(String(255))
    notes = Column(Text)
    updated_by = Column(String(255))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    record = relationship("ExtractedRecord", back_populates="status_updates")
