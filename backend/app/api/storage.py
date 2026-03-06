"""
Storage API - Storage Statistics and Limits
"""

from fastapi import APIRouter
from pydantic import BaseModel

from app.config import settings
from app.utils.logger import logger

# Import ChromaDB service
try:
    from app.services.chromadb_service import get_chromadb_service
    chromadb_available = True
except ImportError:
    chromadb_available = False

router = APIRouter()

# Storage limits
MAX_DOCUMENTS = 50  # Free tier limit
MAX_FILE_SIZE_MB = 50  # Per file limit
ESTIMATED_SIZE_PER_DOC_KB = 250  # Average storage per document


class StorageStats(BaseModel):
    """Storage statistics response"""
    document_count: int
    max_documents: int
    documents_remaining: int
    usage_percent: float
    estimated_storage_kb: int
    max_file_size_mb: int
    warning_threshold: int  # Document count that triggers warning


@router.get("/stats", response_model=StorageStats)
async def get_storage_stats():
    """
    Get storage usage statistics
    
    Returns:
        StorageStats with current usage and limits
    """
    # Get document count
    doc_count = 0
    if settings.use_chromadb and chromadb_available:
        try:
            chromadb_svc = get_chromadb_service()
            collections = chromadb_svc.client.list_collections()
            doc_collections = [c for c in collections if c.name.startswith('medical-docs-')]
            doc_count = len(doc_collections)
        except Exception as e:
            logger.warning(f"Failed to get document count: {e}")
    
    # Calculate statistics
    documents_remaining = max(0, MAX_DOCUMENTS - doc_count)
    usage_percent = round((doc_count / MAX_DOCUMENTS) * 100, 1)
    estimated_storage_kb = doc_count * ESTIMATED_SIZE_PER_DOC_KB
    warning_threshold = int(MAX_DOCUMENTS * 0.8)  # 80% = 40 documents
    
    logger.info(
        "📊 Storage stats requested",
        document_count=doc_count,
        usage_percent=usage_percent
    )
    
    return StorageStats(
        document_count=doc_count,
        max_documents=MAX_DOCUMENTS,
        documents_remaining=documents_remaining,
        usage_percent=usage_percent,
        estimated_storage_kb=estimated_storage_kb,
        max_file_size_mb=MAX_FILE_SIZE_MB,
        warning_threshold=warning_threshold
    )
