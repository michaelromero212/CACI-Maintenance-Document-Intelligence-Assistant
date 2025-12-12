"""Report generation endpoints."""

from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from db.database import get_db
from models.models import Document, ExtractedRecord, Anomaly
from models.schemas import SummaryReport, CAPReport
from reports.cap_generator import CAPGenerator

router = APIRouter()


@router.get("/report/summary", response_model=SummaryReport)
async def get_summary_report(
    document_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Generate a summary report for a document.
    
    Includes status breakdown, priority distribution,
    cost estimates, and anomaly summary.
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    records = db.query(ExtractedRecord).filter(
        ExtractedRecord.document_id == document_id
    ).all()
    
    # Status breakdown
    status_breakdown = {}
    for record in records:
        status = record.status or "unknown"
        status_breakdown[status] = status_breakdown.get(status, 0) + 1
    
    # Priority breakdown
    priority_breakdown = {}
    for record in records:
        priority = record.priority or "unassigned"
        priority_breakdown[priority] = priority_breakdown.get(priority, 0) + 1
    
    # Total cost estimate
    total_cost = sum(
        float(r.cost_estimate) for r in records 
        if r.cost_estimate is not None
    )
    
    # Date range
    dates = [r.start_date for r in records if r.start_date] + \
            [r.end_date for r in records if r.end_date]
    date_range = None
    if dates:
        date_range = {
            "earliest": str(min(dates)),
            "latest": str(max(dates))
        }
    
    # Anomaly summary
    anomalies = db.query(Anomaly).filter(
        Anomaly.document_id == document_id
    ).all()
    
    anomaly_summary = {
        "total": len(anomalies),
        "resolved": sum(1 for a in anomalies if a.resolved),
        "unresolved": sum(1 for a in anomalies if not a.resolved),
        "by_type": {}
    }
    for anomaly in anomalies:
        atype = anomaly.anomaly_type
        anomaly_summary["by_type"][atype] = anomaly_summary["by_type"].get(atype, 0) + 1
    
    return SummaryReport(
        document_id=document.id,
        filename=document.filename,
        total_records=len(records),
        status_breakdown=status_breakdown,
        priority_breakdown=priority_breakdown,
        total_cost_estimate=total_cost if total_cost > 0 else None,
        date_range=date_range,
        anomaly_summary=anomaly_summary,
        generated_at=datetime.utcnow()
    )


@router.get("/report/cap", response_model=CAPReport)
async def generate_cap_report(
    document_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Generate a Corrective Action Plan (CAP) for a document.
    
    Uses LLM to create a structured engineering document
    with findings, recommendations, and action items.
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    records = db.query(ExtractedRecord).filter(
        ExtractedRecord.document_id == document_id
    ).all()
    
    if not records:
        raise HTTPException(
            status_code=400,
            detail="No records found for this document. Please process the document first."
        )
    
    generator = CAPGenerator()
    markdown_content = await generator.generate(document, records)
    
    return CAPReport(
        document_id=document.id,
        generated_at=datetime.utcnow(),
        markdown_content=markdown_content
    )
