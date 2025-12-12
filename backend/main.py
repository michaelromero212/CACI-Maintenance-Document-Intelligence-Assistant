"""
Maintenance Document Intelligence Assistant (MDIA)
FastAPI Backend Application
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.database import engine, Base
from api.routes import upload, documents, ingest, legacy, status, reports


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup: Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown: cleanup if needed


app = FastAPI(
    title="MDIA - Maintenance Document Intelligence Assistant",
    description="AI-powered maintenance document processing and workflow modernization",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router, tags=["Upload"])
app.include_router(documents.router, tags=["Documents"])
app.include_router(ingest.router, tags=["Ingestion"])
app.include_router(legacy.router, tags=["Legacy Conversion"])
app.include_router(status.router, tags=["Status"])
app.include_router(reports.router, tags=["Reports"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "MDIA Backend",
        "version": "1.0.0"
    }
