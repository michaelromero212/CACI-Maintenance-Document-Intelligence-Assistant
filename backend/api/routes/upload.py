"""File upload endpoint."""

import os
import uuid
import aiofiles
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db
from models.models import Document
from models.schemas import DocumentResponse

router = APIRouter()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/app/uploads")
ALLOWED_EXTENSIONS = {".pdf", ".xlsx", ".xls", ".csv", ".txt", ".log"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


def get_file_extension(filename: str) -> str:
    """Extract file extension."""
    return os.path.splitext(filename)[1].lower()


@router.post("/upload", response_model=DocumentResponse)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a document for processing.
    
    Accepts PDF, Excel, CSV, and log files.
    Returns document metadata with assigned ID.
    """
    # Validate file extension
    ext = get_file_extension(file.filename)
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Supported: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Read file content
    content = await file.read()
    file_size = len(content)
    
    # Validate file size
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    # Generate unique filename
    file_id = uuid.uuid4()
    safe_filename = f"{file_id}{ext}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    
    # Ensure upload directory exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(content)
    
    # Determine file type category
    file_type_map = {
        ".pdf": "pdf",
        ".xlsx": "excel",
        ".xls": "excel",
        ".csv": "csv",
        ".txt": "text",
        ".log": "log"
    }
    file_type = file_type_map.get(ext, "unknown")
    
    # Create database record
    document = Document(
        id=file_id,
        filename=file.filename,
        file_type=file_type,
        file_size=file_size,
        processing_status="uploaded"
    )
    
    db.add(document)
    db.commit()
    db.refresh(document)
    
    return DocumentResponse(
        id=document.id,
        filename=document.filename,
        file_type=document.file_type,
        file_size=document.file_size,
        upload_date=document.upload_date,
        processed=document.processed,
        processing_status=document.processing_status,
        record_count=0,
        anomaly_count=0
    )
