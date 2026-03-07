"""
Upload API - Document Upload and Processing
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, status
from typing import Optional
import uuid
import PyPDF2
import io

from ..models.responses import UploadResponse
from ..services import s3_service, opensearch_service, embedding_service
from ..config import settings
from ..utils.logger import logger

# Import ChromaDB service (used when USE_CHROMADB=true)
try:
    from ..services.chromadb_service import get_chromadb_service
    chromadb_available = True
except ImportError:
    chromadb_available = False

router = APIRouter()

# Document storage limits for free tier
MAX_DOCUMENTS = 50  # Render.com free tier limit


async def get_document_count() -> int:
    """Get total number of documents stored in ChromaDB"""
    if settings.use_chromadb and chromadb_available:
        try:
            chromadb_svc = get_chromadb_service()
            collections = chromadb_svc.client.list_collections()
            # Each document has its own collection: medical-docs-{document_id}
            doc_collections = [c for c in collections if c.name.startswith('medical-docs-')]
            return len(doc_collections)
        except Exception as e:
            logger.warning(f"Failed to get document count: {e}")
            return 0
    return 0


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = None
):
    """
    Upload and process a PDF document
    
    For demo: Returns success without processing since AWS services are not configured
    """
    request_id = str(uuid.uuid4())
    document_id = f"doc_{uuid.uuid4().hex[:12]}"
    
    logger.info(
        "📤 Upload request received (demo mode)",
        request_id=request_id,
        filename=file.filename,
        content_type=file.content_type
    )
    
    # For demo: return success response without processing
    return UploadResponse(
        document_id=document_id,
        filename=file.filename or "document.pdf",
        status="success",
        message="Document uploaded successfully (demo mode - processing disabled)",
        pages=0,
        chunks=0
    )
