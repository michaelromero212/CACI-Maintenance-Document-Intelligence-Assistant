"""Document ingestion endpoint."""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from db.database import get_db
from models.models import Document
from models.schemas import DocumentResponse
from services.pipeline import IngestionPipeline

router = APIRouter()


@router.post("/ingest/{document_id}")
async def ingest_document(
    document_id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Trigger document ingestion pipeline.
    
    Extracts text, runs LLM extraction, normalizes data,
    detects anomalies, and stores records.
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document.processing_status == "processing":
        raise HTTPException(status_code=400, detail="Document is already being processed")
    
    # Update status
    document.processing_status = "processing"
    db.commit()
    
    # Run pipeline in background
    background_tasks.add_task(run_ingestion_pipeline, document_id)
    
    return {
        "message": "Ingestion started",
        "document_id": str(document_id),
        "status": "processing"
    }


async def run_ingestion_pipeline(document_id: UUID):
    """Background task to run the ingestion pipeline."""
    from db.database import SessionLocal
    
    db = SessionLocal()
    try:
        pipeline = IngestionPipeline(db)
        await pipeline.process_document(document_id)
    except Exception as e:
        # Update document status on error
        document = db.query(Document).filter(Document.id == document_id).first()
        if document:
            document.processing_status = f"error: {str(e)[:100]}"
            db.commit()
    finally:
        db.close()
