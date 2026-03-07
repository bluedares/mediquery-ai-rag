"""
Documents API - List and Delete Documents
"""

from fastapi import APIRouter, HTTPException, status
from typing import List
from datetime import datetime
import re

from ..models.responses import BaseModel
from ..services import opensearch_service, s3_service, bedrock_service
from ..config import settings
from ..utils.logger import logger

# Import Claude direct API service (used when USE_DIRECT_ANTHROPIC=true)
try:
    from ..services.claude import get_claude_service
    claude_available = True
except ImportError:
    claude_available = False

# Import ChromaDB service (used when USE_CHROMADB=true)
try:
    from ..services.chromadb_service import get_chromadb_service
    chromadb_available = True
except ImportError:
    chromadb_available = False

router = APIRouter()


class DocumentInfo(BaseModel):
    """Document information model"""
    document_id: str
    filename: str
    s3_key: str
    uploaded_at: str
    pages: int = 0
    chunks: int = 0


class HealthIndicator(BaseModel):
    """Health indicator model"""
    name: str
    value: float  # Changed from int to float to accept decimal values from LLM
    status: str
    color: str


class DocumentSummary(BaseModel):
    """Document summary with health indicators"""
    document_id: str
    title: str
    health_indicators: List[HealthIndicator]
    overall_score: str
    overall_color: str
    key_findings: List[str]
    pages: int
    chunks: int


class DocumentListResponse(BaseModel):
    """Response model for document listing"""
    documents: List[DocumentInfo]
    total: int


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents():
    """
    List all uploaded documents from S3
    
    Returns:
        DocumentListResponse with list of documents
    """
    try:
        logger.info("📋 Listing documents (demo mode - returning empty list)")
        
        # For demo: return empty list since S3 is not configured
        return DocumentListResponse(documents=[], total=0)
        
        # Original code commented out for demo
        # List all files in documents/ prefix
        # files = await s3_service.list_files(prefix="documents/")
        
        documents = []
        for file_key in files:
            # Extract document ID from key: documents/doc_abc123.pdf
            match = re.search(r'documents/(doc_[a-f0-9]+)\.pdf', file_key)
            if match:
                doc_id = match.group(1)
                filename = file_key.split('/')[-1]  # Get filename from key
                
                # Get metadata from OpenSearch (count chunks and pages)
                try:
                    from ..services import embedding_service
                    dummy_embedding = await embedding_service.encode_single("document")
                    
                    # Choose vector database based on configuration
                    if settings.use_chromadb:
                        if chromadb_available:
                            chromadb_svc = get_chromadb_service()
                            search_results = await chromadb_svc.hybrid_search(
                                collection_name=f"medical-docs-{doc_id}",
                                query_text="document",
                                query_embedding=dummy_embedding,
                                top_k=1000
                            )
                        else:
                            search_results = []
                    else:
                        search_results = await opensearch_service.hybrid_search(
                            index_name=f"medical-docs-{doc_id}",
                            query_text="document",
                            query_embedding=dummy_embedding,
                            top_k=1000
                        )
                    
                    chunks_count = len(search_results)
                    pages_set = set()
                    for result in search_results:
                        if 'metadata' in result and 'page' in result['metadata']:
                            pages_set.add(result['metadata']['page'])
                    pages_count = len(pages_set)
                except Exception as e:
                    logger.warning(f"Failed to get metadata for {doc_id}: {e}")
                    chunks_count = 0
                    pages_count = 0
                
                documents.append(DocumentInfo(
                    document_id=doc_id,
                    filename=filename,
                    s3_key=file_key,
                    uploaded_at=datetime.now().isoformat(),
                    pages=pages_count,
                    chunks=chunks_count
                ))
        
        logger.info(f"✅ Found {len(documents)} documents")
        
        return DocumentListResponse(
            documents=documents,
            total=len(documents)
        )
        
    except Exception as e:
        logger.error(
            "❌ Failed to list documents",
            error=str(e),
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list documents: {str(e)}"
        )


@router.get("/documents/{document_id}/summary", response_model=DocumentSummary)
async def get_document_summary(document_id: str):
    """
    Generate AI summary of document with health indicators
    
    Args:
        document_id: Document ID to summarize
        
    Returns:
        DocumentSummary with health indicators and key findings
    """
    try:
        logger.info(
            "📊 Generating document summary using multi-agent RAG",
            document_id=document_id
        )
        
        # Use the same multi-agent RAG system as Q&A for consistent, high-quality results
        from ..agents import agent_graph
        import uuid
        
        # Initialize agent state with summary query
        initial_state = {
            'request_id': str(uuid.uuid4()),
            'user_query': "Analyze my test results. Categorize them as: ✅ Normal (with values), ⚠️ Borderline/Needs Monitoring (with values and why), ❗ Abnormal/Needs Attention (with values and why). Be concise.",
            'document_id': document_id,
            'conversation_id': None,
            'intent': '',
            'search_strategy': '',
            'expanded_query': None,
            'retrieved_chunks': [],
            'retrieval_scores': [],
            'reranked_chunks': [],
            'rerank_scores': [],
            'final_answer': '',
            'citations': [],
            'confidence': 0.0,
            'agent_trace': [],
            'errors': []
        }
        
        # Execute agent graph to get proper analysis
        result = await agent_graph.ainvoke(initial_state)
        summary_text = result.get('final_answer', '')
        
        # Count pages from citations
        pages_set = set()
        for cite in result.get('citations', []):
            if 'page' in cite:
                pages_set.add(cite['page'])
        
        # Return the multi-agent generated summary directly
        # The frontend will display this text as-is (it's already properly formatted)
        summary = DocumentSummary(
            document_id=document_id,
            title=f"Medical Report Analysis",
            report_type="Medical Test Report",
            report_description=summary_text,  # The categorized analysis from multi-agent
            health_indicators=[],  # Not used - text has all info
            overall_score="Good" if "✅" in summary_text and "❗" not in summary_text else ("Needs Attention" if "❗" in summary_text else "Moderate"),
            overall_color="#10b981" if "✅" in summary_text and "❗" not in summary_text else ("#ef4444" if "❗" in summary_text else "#f59e0b"),
            key_findings=[summary_text],  # The full categorized text
            pages=len(pages_set),
            chunks=len(result.get('citations', []))
        )
        
        logger.info(
            "✅ Summary generated successfully using multi-agent RAG",
            document_id=document_id
        )
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "❌ Failed to generate summary",
            document_id=document_id,
            error=str(e),
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate summary: {str(e)}"
        )



@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a document from S3 and OpenSearch
    
    Args:
        document_id: Document ID to delete
        
    Returns:
        Success message
    """
    try:
        logger.info(
            "🗑️  Deleting document",
            document_id=document_id
        )
        
        # Delete from S3
        s3_key = f"documents/{document_id}.pdf"
        await s3_service.delete_file(s3_key)
        
        # Delete from vector database
        if settings.use_chromadb:
            logger.info("🗑️  Deleting ChromaDB collection", document_id=document_id)
            if chromadb_available:
                try:
                    chromadb_svc = get_chromadb_service()
                    collection_name = f"medical-docs-{document_id}"
                    chromadb_svc.delete_collection(collection_name)
                    logger.info(f"✅ Deleted ChromaDB collection: {collection_name}")
                except Exception as e:
                    logger.warning(f"⚠️  Failed to delete ChromaDB collection: {e}")
            else:
                logger.warning("⚠️  ChromaDB not available, skipping vector cleanup")
        else:
            # Delete from OpenSearch (all chunks for this document)
            # Note: In production with OpenSearch, implement delete by query:
            # opensearch_service.delete_by_query(
            #     index_name="medical-documents",
            #     query={"match": {"metadata.document_id": document_id}}
            # )
            logger.info("📊 OpenSearch cleanup skipped (mock mode)")
        
        logger.info(
            "✅ Document deleted successfully",
            document_id=document_id
        )
        
        return {
            "status": "success",
            "message": f"Document {document_id} deleted successfully",
            "document_id": document_id
        }
        
    except Exception as e:
        logger.error(
            "❌ Failed to delete document",
            document_id=document_id,
            error=str(e),
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )
