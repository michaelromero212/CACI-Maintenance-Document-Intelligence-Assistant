"""Document listing and retrieval endpoints."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from db.database import get_db
from models.models import Document, ExtractedRecord, Anomaly
from models.schemas import DocumentResponse, DocumentDetail, RecordResponse

router = APIRouter()


@router.get("/documents", response_model=List[DocumentResponse])
async def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    processed: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    List all uploaded documents.
    
    Supports pagination and filtering by processed status.
    """
    query = db.query(Document)
    
    if processed is not None:
        query = query.filter(Document.processed == processed)
    
    documents = query.order_by(Document.upload_date.desc()).offset(skip).limit(limit).all()
    
    result = []
    for doc in documents:
        record_count = db.query(func.count(ExtractedRecord.id)).filter(
            ExtractedRecord.document_id == doc.id
        ).scalar()
        anomaly_count = db.query(func.count(Anomaly.id)).filter(
            Anomaly.document_id == doc.id
        ).scalar()
        
        result.append(DocumentResponse(
            id=doc.id,
            filename=doc.filename,
            file_type=doc.file_type,
            file_size=doc.file_size,
            upload_date=doc.upload_date,
            processed=doc.processed,
            processing_status=doc.processing_status,
            record_count=record_count,
            anomaly_count=anomaly_count
        ))
    
    return result


@router.get("/documents/{document_id}", response_model=DocumentDetail)
async def get_document(
    document_id: UUID,
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific document."""
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    record_count = db.query(func.count(ExtractedRecord.id)).filter(
        ExtractedRecord.document_id == document.id
    ).scalar()
    anomaly_count = db.query(func.count(Anomaly.id)).filter(
        Anomaly.document_id == document.id
    ).scalar()
    
    return DocumentDetail(
        id=document.id,
        filename=document.filename,
        file_type=document.file_type,
        file_size=document.file_size,
        upload_date=document.upload_date,
        processed=document.processed,
        processing_status=document.processing_status,
        raw_text=document.raw_text,
        record_count=record_count,
        anomaly_count=anomaly_count
    )


@router.get("/records", response_model=List[RecordResponse])
async def list_records(
    document_id: Optional[UUID] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    List extracted records with optional filters.
    """
    query = db.query(ExtractedRecord)
    
    if document_id:
        query = query.filter(ExtractedRecord.document_id == document_id)
    if status:
        query = query.filter(ExtractedRecord.status == status)
    if priority:
        query = query.filter(ExtractedRecord.priority == priority)
    
    records = query.order_by(ExtractedRecord.created_at.desc()).offset(skip).limit(limit).all()
    
    return [RecordResponse.model_validate(record) for record in records]


@router.get("/record/{record_id}", response_model=RecordResponse)
async def get_record(
    record_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific extracted record."""
    record = db.query(ExtractedRecord).filter(ExtractedRecord.id == record_id).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    return RecordResponse.model_validate(record)
