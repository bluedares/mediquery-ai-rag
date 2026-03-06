"""
Upload API - Document Upload and Processing
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, status
from typing import Optional
import uuid
import PyPDF2
import io

from app.models.responses import UploadResponse
from app.services import s3_service, opensearch_service, embedding_service
from app.config import settings
from app.utils.logger import logger

# Import ChromaDB service (used when USE_CHROMADB=true)
try:
    from app.services.chromadb_service import get_chromadb_service
    chromadb_available = True
except ImportError:
    chromadb_available = False

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = None
):
    """
    Upload and process a PDF document
    
    Steps:
    1. Validate PDF file
    2. Extract text from PDF
    3. Generate embeddings
    4. Store in S3
    5. Index in OpenSearch
    
    Args:
        file: PDF file to upload
        title: Optional document title
        
    Returns:
        UploadResponse with document ID and processing status
    """
    request_id = str(uuid.uuid4())
    
    logger.info(
        "📤 Upload request received",
        request_id=request_id,
        filename=file.filename,
        content_type=file.content_type
    )
    
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported"
        )
    
    try:
        # Read file content
        content = await file.read()
        
        # Extract text from PDF
        logger.info("📄 Extracting text from PDF", request_id=request_id)
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
        
        # Extract text from all pages
        text_chunks = []
        for page_num, page in enumerate(pdf_reader.pages):
            text = page.extract_text()
            if text.strip():
                # Split into chunks (simple chunking - 500 chars with overlap)
                chunk_size = 500
                overlap = 50
                
                for i in range(0, len(text), chunk_size - overlap):
                    chunk = text[i:i + chunk_size]
                    if chunk.strip():
                        text_chunks.append({
                            'text': chunk.strip(),
                            'page': page_num + 1,
                            'chunk_id': f"chunk_{page_num}_{i}"
                        })
        
        logger.info(
            f"✅ Extracted {len(text_chunks)} chunks from {len(pdf_reader.pages)} pages",
            request_id=request_id
        )
        
        # Generate document ID
        document_id = f"doc_{uuid.uuid4().hex[:12]}"
        
        # Upload to S3
        logger.info("☁️  Uploading to S3", request_id=request_id, document_id=document_id)
        await s3_service.upload_file(
            file_obj=io.BytesIO(content),
            key=f"documents/{document_id}.pdf",
            content_type="application/pdf"
        )
        
        # Generate embeddings and index in vector database
        logger.info("🔢 Generating embeddings", request_id=request_id)
        
        # Choose vector database based on configuration
        if settings.use_chromadb:
            logger.info("� Using ChromaDB for vector storage", request_id=request_id)
            if not chromadb_available:
                raise Exception("ChromaDB not available. Install chromadb package.")
            
            chromadb_svc = get_chromadb_service()
            collection_name = f"medical-docs-{document_id}"
            
            for chunk in text_chunks:
                # Generate embedding
                embedding = await embedding_service.encode_single(chunk['text'])
                
                # Index in ChromaDB
                chromadb_svc.index_document(
                    collection_name=collection_name,
                    doc_id=f"{document_id}_{chunk['chunk_id']}",
                    text=chunk['text'],
                    embedding=embedding,
                    metadata={
                        'document_id': document_id,
                        'page': chunk['page'],
                        'chunk_id': chunk['chunk_id'],
                        'title': title or file.filename
                    }
                )
        else:
            logger.info("📊 Using OpenSearch for vector storage", request_id=request_id)
            
            for chunk in text_chunks:
                # Generate embedding
                embedding = await embedding_service.encode_single(chunk['text'])
                
                # Index in OpenSearch
                opensearch_service.index_document(
                    index_name="medical-documents",
                    doc_id=f"{document_id}_{chunk['chunk_id']}",
                    text=chunk['text'],
                    embedding=embedding,
                    metadata={
                        'document_id': document_id,
                        'page': chunk['page'],
                        'chunk_id': chunk['chunk_id'],
                        'title': title or file.filename
                    }
                )
        
        logger.info(
            "✅ Document processed successfully",
            request_id=request_id,
            document_id=document_id,
            chunks=len(text_chunks)
        )
        
        return UploadResponse(
            document_id=document_id,
            filename=file.filename,
            pages=len(pdf_reader.pages),
            chunks=len(text_chunks),
            status="success",
            message=f"Processed {len(text_chunks)} chunks from {len(pdf_reader.pages)} pages"
        )
        
    except PyPDF2.errors.PdfReadError as e:
        logger.error(
            "❌ PDF parsing failed",
            request_id=request_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid PDF file: {str(e)}"
        )
    except Exception as e:
        logger.error(
            "❌ Upload failed",
            request_id=request_id,
            error=str(e),
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )
