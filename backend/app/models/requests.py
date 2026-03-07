"""
Request Models - Pydantic schemas for API requests
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


class QueryRequest(BaseModel):
    """Request model for document query"""
    
    query: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="Natural language query about the document"
    )
    document_id: str = Field(
        ...,
        description="ID of the document to query"
    )
    conversation_id: Optional[str] = Field(
        None,
        description="Conversation ID for follow-up questions"
    )
    include_trace: bool = Field(
        True,
        description="Include agent trace in response"
    )
    
    @validator('query')
    def query_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Query cannot be empty')
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What are the primary endpoints of this trial?",
                "document_id": "doc_123",
                "include_trace": True
            }
        }


class UploadRequest(BaseModel):
    """Metadata for document upload"""
    
    document_type: str = Field(
        "clinical_trial",
        description="Type of medical document"
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Tags for categorization"
    )
    metadata: Optional[dict] = Field(
        None,
        description="Additional metadata"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "document_type": "clinical_trial",
                "tags": ["phase_3", "oncology"],
                "metadata": {
                    "trial_id": "NCT12345678",
                    "sponsor": "Example Pharma"
                }
            }
        }


class DocumentFilter(BaseModel):
    """Filter for document listing"""
    
    document_type: Optional[str] = None
    tags: Optional[List[str]] = None
    uploaded_after: Optional[datetime] = None
    uploaded_before: Optional[datetime] = None
    search_term: Optional[str] = None
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)
    
    class Config:
        json_schema_extra = {
            "example": {
                "document_type": "clinical_trial",
                "tags": ["oncology"],
                "page": 1,
                "limit": 20
            }
        }
