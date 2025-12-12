"""Legacy Excel conversion endpoint."""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid

from db.database import get_db
from models.schemas import LegacyConversionResult
from ingestion.legacy_converter import LegacyConverter

router = APIRouter()


@router.post("/legacy/convert", response_model=LegacyConversionResult)
async def convert_legacy_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Convert a legacy MSC-style Excel file to normalized format.
    
    Auto-maps unpredictable column labels to standardized schema:
    - component, system, priority, maint_action
    - cost_estimate, start_date, end_date, notes
    
    Returns normalized records and ingestion summary.
    """
    # Validate file type
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=400,
            detail="Only Excel files (.xlsx, .xls) are supported"
        )
    
    try:
        content = await file.read()
        
        converter = LegacyConverter(db)
        result = await converter.convert(
            file_content=content,
            filename=file.filename
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Conversion failed: {str(e)}"
        )
