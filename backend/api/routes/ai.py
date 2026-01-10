"""AI-related API endpoints for LLM status and chat."""

import os
import time
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from llm.client import LLMClient
from llm.prompts import SUMMARY_TEMPLATE


router = APIRouter()

# Global LLM client instance
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """Get or create LLM client singleton."""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client


# Request/Response Models
class AIStatusResponse(BaseModel):
    """AI model status response."""
    status: str  # "connected", "disconnected", "error"
    model: str
    has_token: bool
    response_time_ms: Optional[float] = None
    last_check: str
    message: str


class AIChatRequest(BaseModel):
    """Request for AI chat."""
    message: str
    document_id: Optional[str] = None
    context: Optional[str] = "maintenance"


class AIChatResponse(BaseModel):
    """Response from AI chat."""
    response: str
    tokens_used: Optional[int] = None
    processing_time_ms: float


class AIAnalyzeRequest(BaseModel):
    """Request for document analysis."""
    document_id: str
    analysis_type: str = "summary"  # "summary", "risks", "priorities"


class AIAnalyzeResponse(BaseModel):
    """Response from document analysis."""
    document_id: str
    analysis_type: str
    analysis: str
    processing_time_ms: float


@router.get("/ai/status", response_model=AIStatusResponse)
async def get_ai_status():
    """
    Check AI model status and connectivity.
    
    Returns detailed status including:
    - Connection status (connected/disconnected/error)
    - Model name
    - Whether HF token is configured
    - Response time for last health check
    """
    client = get_llm_client()
    has_token = bool(os.getenv("HF_TOKEN"))
    
    # Time the health check
    start_time = time.time()
    
    try:
        is_available = client.is_available()
        response_time_ms = (time.time() - start_time) * 1000
        
        if is_available:
            return AIStatusResponse(
                status="connected",
                model=client.model,
                has_token=has_token,
                response_time_ms=round(response_time_ms, 2),
                last_check=datetime.now(timezone.utc).isoformat(),
                message="AI model is operational and ready"
            )
        else:
            return AIStatusResponse(
                status="disconnected",
                model=client.model,
                has_token=has_token,
                response_time_ms=round(response_time_ms, 2),
                last_check=datetime.now(timezone.utc).isoformat(),
                message="AI model is not responding. Check HF_TOKEN configuration."
            )
    except Exception as e:
        response_time_ms = (time.time() - start_time) * 1000
        return AIStatusResponse(
            status="error",
            model=client.model,
            has_token=has_token,
            response_time_ms=round(response_time_ms, 2),
            last_check=datetime.now(timezone.utc).isoformat(),
            message=f"Error checking AI status: {str(e)}"
        )


@router.post("/ai/chat", response_model=AIChatResponse)
async def ai_chat(request: AIChatRequest):
    """
    Send a message to the AI assistant.
    
    Supports optional document context for document-aware responses.
    """
    client = get_llm_client()
    
    start_time = time.time()
    
    # Build system prompt based on context
    system_prompt = """You are MDIA, a Maintenance Document Intelligence Assistant. 
You help maintenance teams with:
- Analyzing maintenance documents and records
- Identifying priority items and risks
- Providing recommendations for maintenance actions
- Answering questions about maintenance procedures

Be concise, professional, and helpful. Focus on actionable information."""

    if request.context == "maintenance":
        system_prompt += "\nContext: You are assisting with maritime maintenance documentation for military vessels."
    
    try:
        response = await client.generate(
            prompt=request.message,
            system_prompt=system_prompt,
            max_tokens=1024,
            temperature=0.3
        )
        
        processing_time_ms = (time.time() - start_time) * 1000
        
        if not response:
            raise HTTPException(
                status_code=503,
                detail="AI model did not return a response. The service may be temporarily unavailable."
            )
        
        return AIChatResponse(
            response=response,
            tokens_used=None,  # HF API doesn't always return this
            processing_time_ms=round(processing_time_ms, 2)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI chat error: {str(e)}"
        )


@router.post("/ai/analyze", response_model=AIAnalyzeResponse)
async def ai_analyze(request: AIAnalyzeRequest):
    """
    Perform AI analysis on a document.
    
    Analysis types:
    - summary: Generate a summary of the document
    - risks: Identify potential risks and issues
    - priorities: Highlight priority items
    """
    from db.database import SessionLocal
    from models.models import Document, ExtractedRecord
    
    client = get_llm_client()
    start_time = time.time()
    
    # Fetch document and records
    db = SessionLocal()
    try:
        document = db.query(Document).filter(Document.id == request.document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        records = db.query(ExtractedRecord).filter(
            ExtractedRecord.document_id == request.document_id
        ).all()
        
        # Build context from records
        record_context = []
        for r in records:
            record_context.append(
                f"- Component: {r.component or 'N/A'}, "
                f"Priority: {r.priority or 'N/A'}, "
                f"Action: {r.maint_action or 'N/A'}, "
                f"Status: {r.status or 'N/A'}"
            )
        
        records_text = "\n".join(record_context) if record_context else "No records extracted."
        
    finally:
        db.close()
    
    # Build analysis prompt based on type
    if request.analysis_type == "summary":
        prompt = f"""Summarize the following maintenance document and its records:

Document: {document.filename}
Records:
{records_text}

Provide a brief executive summary (3-5 sentences) covering:
1. Total maintenance items
2. Priority distribution
3. Key concerns or patterns"""

    elif request.analysis_type == "risks":
        prompt = f"""Analyze the following maintenance records for potential risks:

Document: {document.filename}
Records:
{records_text}

Identify:
1. High-priority items requiring immediate attention
2. Potential equipment failure risks
3. Resource or scheduling concerns
4. Recommended preventive actions"""

    elif request.analysis_type == "priorities":
        prompt = f"""Prioritize the following maintenance items:

Document: {document.filename}
Records:
{records_text}

Provide a prioritized action list:
1. Rank items by urgency
2. Explain prioritization rationale
3. Suggest optimal sequencing"""

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid analysis_type: {request.analysis_type}. "
                   f"Must be 'summary', 'risks', or 'priorities'."
        )
    
    try:
        system_prompt = "You are a maintenance document analyst. Provide clear, actionable analysis."
        
        response = await client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=1024,
            temperature=0.2
        )
        
        processing_time_ms = (time.time() - start_time) * 1000
        
        if not response:
            raise HTTPException(
                status_code=503,
                detail="AI analysis failed. The service may be temporarily unavailable."
            )
        
        return AIAnalyzeResponse(
            document_id=request.document_id,
            analysis_type=request.analysis_type,
            analysis=response,
            processing_time_ms=round(processing_time_ms, 2)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI analysis error: {str(e)}"
        )
