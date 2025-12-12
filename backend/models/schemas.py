"""Pydantic schemas for API request/response validation."""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field


# Document schemas
class DocumentBase(BaseModel):
    filename: str
    file_type: str
    file_size: int


class DocumentCreate(DocumentBase):
    pass


class DocumentResponse(DocumentBase):
    id: UUID
    upload_date: datetime
    processed: bool
    processing_status: str
    record_count: Optional[int] = 0
    anomaly_count: Optional[int] = 0

    class Config:
        from_attributes = True


class DocumentDetail(DocumentResponse):
    raw_text: Optional[str] = None


# Extracted record schemas
class RecordBase(BaseModel):
    component: Optional[str] = None
    system: Optional[str] = None
    failure_type: Optional[str] = None
    maint_action: Optional[str] = None
    priority: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    cost_estimate: Optional[Decimal] = None
    summary_notes: Optional[str] = None


class RecordCreate(RecordBase):
    document_id: UUID


class RecordUpdate(BaseModel):
    component: Optional[str] = None
    system: Optional[str] = None
    failure_type: Optional[str] = None
    maint_action: Optional[str] = None
    priority: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    cost_estimate: Optional[Decimal] = None
    summary_notes: Optional[str] = None


class RecordResponse(RecordBase):
    id: UUID
    document_id: UUID
    status: str
    assigned_to: Optional[str] = None
    confidence_score: Optional[Decimal] = None
    extraction_method: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Status update schemas
class StatusUpdateRequest(BaseModel):
    status: str = Field(..., pattern="^(open|in-progress|awaiting-parts|complete)$")
    assigned_to: Optional[str] = None
    notes: Optional[str] = None


class StatusUpdateResponse(BaseModel):
    id: UUID
    record_id: UUID
    previous_status: Optional[str]
    new_status: str
    assigned_to: Optional[str]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Anomaly schemas
class AnomalyResponse(BaseModel):
    id: UUID
    record_id: Optional[UUID]
    document_id: UUID
    anomaly_type: str
    severity: str
    description: str
    field_name: Optional[str]
    field_value: Optional[str]
    suggested_fix: Optional[str]
    resolved: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Status overview
class StatusCount(BaseModel):
    status: str
    count: int


class StatusOverview(BaseModel):
    total_records: int
    by_status: List[StatusCount]
    by_priority: List[StatusCount]


# Legacy conversion
class LegacyConversionResult(BaseModel):
    success: bool
    document_id: UUID
    records_created: int
    records_with_issues: int
    column_mappings: dict
    message: str


# Report schemas
class SummaryReport(BaseModel):
    document_id: UUID
    filename: str
    total_records: int
    status_breakdown: dict
    priority_breakdown: dict
    total_cost_estimate: Optional[Decimal]
    date_range: Optional[dict]
    anomaly_summary: dict
    generated_at: datetime


class CAPReport(BaseModel):
    document_id: UUID
    generated_at: datetime
    markdown_content: str
