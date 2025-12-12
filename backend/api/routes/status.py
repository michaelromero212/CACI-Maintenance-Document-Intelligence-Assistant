"""Status management endpoints."""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from db.database import get_db
from models.models import ExtractedRecord, StatusUpdate
from models.schemas import (
    StatusUpdateRequest, StatusUpdateResponse,
    RecordResponse, StatusOverview, StatusCount
)

router = APIRouter()

VALID_STATUSES = {"open", "in-progress", "awaiting-parts", "complete"}


@router.patch("/record/{record_id}/status", response_model=RecordResponse)
async def update_record_status(
    record_id: UUID,
    status_update: StatusUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    Update the status of a maintenance record.
    
    Valid statuses: open, in-progress, awaiting-parts, complete
    """
    record = db.query(ExtractedRecord).filter(ExtractedRecord.id == record_id).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    if status_update.status not in VALID_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Valid options: {', '.join(VALID_STATUSES)}"
        )
    
    # Create status update history entry
    history_entry = StatusUpdate(
        record_id=record.id,
        previous_status=record.status,
        new_status=status_update.status,
        assigned_to=status_update.assigned_to,
        notes=status_update.notes
    )
    db.add(history_entry)
    
    # Update record
    record.status = status_update.status
    if status_update.assigned_to:
        record.assigned_to = status_update.assigned_to
    
    db.commit()
    db.refresh(record)
    
    return RecordResponse.model_validate(record)


@router.get("/status/overview", response_model=StatusOverview)
async def get_status_overview(
    db: Session = Depends(get_db)
):
    """
    Get overview of all record statuses.
    
    Returns counts by status and priority.
    """
    total = db.query(func.count(ExtractedRecord.id)).scalar()
    
    # Count by status
    status_counts = db.query(
        ExtractedRecord.status,
        func.count(ExtractedRecord.id)
    ).group_by(ExtractedRecord.status).all()
    
    by_status = [
        StatusCount(status=s or "unknown", count=c) 
        for s, c in status_counts
    ]
    
    # Count by priority
    priority_counts = db.query(
        ExtractedRecord.priority,
        func.count(ExtractedRecord.id)
    ).group_by(ExtractedRecord.priority).all()
    
    by_priority = [
        StatusCount(status=p or "unassigned", count=c) 
        for p, c in priority_counts
    ]
    
    return StatusOverview(
        total_records=total or 0,
        by_status=by_status,
        by_priority=by_priority
    )


@router.get("/record/{record_id}/history", response_model=List[StatusUpdateResponse])
async def get_status_history(
    record_id: UUID,
    db: Session = Depends(get_db)
):
    """Get status change history for a record."""
    record = db.query(ExtractedRecord).filter(ExtractedRecord.id == record_id).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    history = db.query(StatusUpdate).filter(
        StatusUpdate.record_id == record_id
    ).order_by(StatusUpdate.created_at.desc()).all()
    
    return [StatusUpdateResponse.model_validate(h) for h in history]
