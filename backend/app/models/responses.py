"""
Response Models - Pydantic schemas for API responses
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class Citation(BaseModel):
    """Citation from source document"""
    
    document_id: str
    page: int
    section: Optional[str] = None
    text: str = Field(..., max_length=500)
    relevance_score: float = Field(..., ge=0.0, le=1.0)


class AgentTraceEntry(BaseModel):
    """Single agent execution trace"""
    
    agent: str
    duration_ms: float
    status: str
    timestamp: float
    input_summary: Optional[Dict[str, Any]] = None
    output_summary: Optional[Dict[str, Any]] = None


class QueryResponse(BaseModel):
    """Response model for document query"""
    
    request_id: str
    answer: str
    citations: List[Citation]
    confidence: float = Field(..., ge=0.0, le=1.0)
    processing_time_ms: float
    agent_trace: Optional[List[AgentTraceEntry]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "req_abc123",
                "answer": "The primary endpoints are:\n1. Overall Survival (OS) at 24 months\n2. Progression-Free Survival (PFS)",
                "citations": [
                    {
                        "document_id": "doc_123",
                        "page": 12,
                        "section": "Study Design",
                        "text": "Primary endpoint: OS at 24 months...",
                        "relevance_score": 0.92
                    }
                ],
                "confidence": 0.89,
                "processing_time_ms": 2345.6,
                "agent_trace": [
                    {
                        "agent": "QueryAnalyzerAgent",
                        "duration_ms": 45.2,
                        "status": "success",
                        "timestamp": 1709635200.0
                    }
                ]
            }
        }


class UploadResponse(BaseModel):
    """Response model for document upload"""
    
    document_id: str
    filename: str
    pages: int
    chunks: int
    status: str
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "doc_123",
                "filename": "clinical_trial.pdf",
                "status": "indexed",
                "size_bytes": 2048576,
                "chunks_created": 47,
                "processing_time_ms": 23456.7,
                "message": "Document uploaded and indexed successfully"
            }
        }


class DocumentMetadata(BaseModel):
    """Document metadata"""
    
    document_id: str
    filename: str
    document_type: str
    size_bytes: int
    upload_date: datetime
    chunks: int
    status: str
    tags: List[str] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None


class DocumentSummary(BaseModel):
    """AI-generated summary of document"""
    
    title: str
    pages: int
    chunks: int
    report_type: Optional[str] = None
    report_description: Optional[str] = None
    health_indicators: List[Any]  # Note: HealthIndicator is not defined in the provided code
    overall_score: str
    overall_color: str
    key_findings: List[str] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None


class DocumentResponse(BaseModel):
    """Response model for document listing"""
    
    documents: List[DocumentMetadata]
    total: int
    page: int
    pages: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "documents": [
                    {
                        "document_id": "doc_123",
                        "filename": "trial_protocol.pdf",
                        "document_type": "clinical_trial",
                        "size_bytes": 2048576,
                        "upload_date": "2026-03-05T10:30:00Z",
                        "chunks": 47,
                        "status": "indexed",
                        "tags": ["phase_3", "oncology"]
                    }
                ],
                "total": 156,
                "page": 1,
                "pages": 8
            }
        }


class HealthResponse(BaseModel):
    """Health check response"""
    
    status: str
    version: str
    timestamp: datetime
    services: Dict[str, str]
    debug_mode: bool
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "timestamp": "2026-03-05T14:30:00Z",
                "services": {
                    "bedrock": "available",
                    "opensearch": "available",
                    "s3": "available"
                },
                "debug_mode": True
            }
        }
