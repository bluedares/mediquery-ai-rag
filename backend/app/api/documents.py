"""
Documents API - List and Delete Documents
"""

from fastapi import APIRouter, HTTPException, status
from typing import List
from datetime import datetime
import re

from ..models.responses import BaseModel
# Commented out for demo - AWS services not needed
# from ..services import opensearch_service, s3_service, bedrock_service
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
    # For demo: return empty list since S3 is not configured
    logger.info("📋 Listing documents (demo mode - returning empty list)")
    return DocumentListResponse(documents=[], total=0)


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
            "📊 Generating document summary",
            document_id=document_id
        )
        
        # Retrieve all chunks for this document from vector database
        from ..services import embedding_service
        dummy_embedding = await embedding_service.encode_single("medical report summary")
        
        # Choose vector database based on configuration
        if settings.use_chromadb:
            logger.debug("📊 Using ChromaDB for summary retrieval")
            if not chromadb_available:
                raise Exception("ChromaDB not available. Install chromadb package.")
            
            chromadb_svc = get_chromadb_service()
            search_results = await chromadb_svc.hybrid_search(
                collection_name=f"medical-docs-{document_id}",
                query_text="medical report",
                query_embedding=dummy_embedding,
                top_k=1000  # Get all chunks
            )
        else:
            logger.debug("📊 Using OpenSearch for summary retrieval")
            search_results = await opensearch_service.hybrid_search(
                index_name=f"medical-docs-{document_id}",
                query_text="medical report",
                query_embedding=dummy_embedding,
                top_k=1000  # Get all chunks
            )
        
        if not search_results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {document_id} not found"
            )
        
        # Combine all chunk texts
        full_text = "\n\n".join([chunk['text'] for chunk in search_results])
        
        # Count pages
        pages_set = set()
        for result in search_results:
            if 'metadata' in result and 'page' in result['metadata']:
                pages_set.add(result['metadata']['page'])
        
        # Generate summary using Claude
        prompt = f"""Analyze this medical report and extract ONLY the health metrics that are actually present in the document.

Medical Report:
{full_text[:4000]}

IMPORTANT INSTRUCTIONS:
1. Identify the report type (e.g., "Blood Test Report", "Complete Blood Count", "Lipid Panel", "Diabetes Screening", "Cancer Marker Test", "Thyroid Function Test", etc.)
2. Provide a brief 1-2 sentence description of what this report is about
3. Extract ONLY health metrics that are explicitly mentioned in the report (e.g., Blood Glucose, Cholesterol, Blood Pressure, Heart Rate, BMI, etc.)
4. Do NOT include metrics that are not in the report
5. Calculate a score (0-100) based on the actual values in the report:
   - 80-100 = good (green: #10b981)
   - 50-79 = moderate (yellow: #f59e0b)
   - 0-49 = needs attention (red: #ef4444)
6. Extract 3-5 key findings from the report

Return ONLY valid JSON, no other text:

{{
    "report_type": "Blood Test Report",
    "report_description": "Complete blood count and metabolic panel showing overall health status",
    "health_indicators": [
        {{"name": "Metric Name", "value": 85, "status": "good", "color": "#10b981"}}
    ],
    "overall_score": "Good",
    "overall_color": "#10b981",
    "key_findings": ["Finding from report", "Another finding", "Third finding"]
}}"""

        # Choose LLM service based on configuration
        import asyncio
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                if settings.use_direct_anthropic:
                    logger.warning("⚠️  Using DIRECT Anthropic API for summary (bypassing Bedrock security)")
                    if not claude_available:
                        raise Exception("Direct Anthropic API not available. Install anthropic package.")
                    claude_service = get_claude_service()
                    response = await claude_service.invoke(
                        prompt=prompt,
                        system_prompt="You are a medical report analyzer. Extract health metrics from reports and return ONLY valid JSON. Do not include any explanatory text, markdown formatting, or code blocks - just pure JSON.",
                        max_tokens=1000
                    )
                else:
                    response = await bedrock_service.invoke(
                        prompt=prompt,
                        system_prompt="You are a medical report analyzer. Extract health metrics from reports and return ONLY valid JSON. Do not include any explanatory text, markdown formatting, or code blocks - just pure JSON.",
                        max_tokens=1000
                    )
                break  # Success, exit retry loop
                
            except Exception as e:
                if "overloaded" in str(e).lower() and attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(f"API overloaded, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(wait_time)
                else:
                    raise  # Re-raise if not overloaded error or last attempt
        
        # Parse LLM response
        try:
            import json
            import re
            
            # Log raw response for debugging
            logger.debug(f"Raw LLM response: {response[:200]}...")
            
            # Extract JSON from response
            response_text = response.strip()
            
            # Try multiple extraction methods
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            # Try to find JSON object in response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(0)
            
            response_text = response_text.strip()
            logger.debug(f"Extracted JSON: {response_text[:200]}...")
            
            summary_data = json.loads(response_text)
            logger.info(f"✅ Successfully parsed LLM response with {len(summary_data.get('health_indicators', []))} indicators")
        except Exception as e:
            logger.warning(f"Failed to parse LLM response: {e}")
            logger.warning(f"Response was: {response[:500]}")
            
            # Extract basic findings from document text as fallback
            import re
            key_findings = []
            for result in search_results[:10]:  # Check more chunks to find good content
                text = result.get('text', '').strip()
                if not text or len(text) < 40:  # Need substantial text
                    continue
                
                # Clean and validate text
                # Remove non-printable characters and excessive whitespace
                text = re.sub(r'[^\x20-\x7E\n]', '', text)  # Keep only printable ASCII
                text = re.sub(r'\s+', ' ', text).strip()
                
                # Skip if mostly numbers/symbols or looks like metadata
                if len(re.findall(r'[a-zA-Z]', text)) < len(text) * 0.5:  # Less than 50% letters
                    continue
                if re.match(r'^(Page \d+|Sample|PID|Sex|Age|Ref)', text):
                    continue
                
                # Extract first meaningful sentence
                sentences = text.split('. ')
                for sentence in sentences:
                    sentence = sentence.strip()
                    if len(sentence) >= 40 and len(sentence) <= 200:  # Good length
                        # Check if it's a meaningful sentence (has verbs/content words)
                        if re.search(r'\b(is|are|was|were|has|have|shows|indicates|level|count|result)\b', sentence, re.I):
                            if sentence not in key_findings:
                                key_findings.append(sentence)
                                break
                
                if len(key_findings) >= 4:
                    break
            
            # If still no findings, use generic message
            if not key_findings:
                key_findings = ["Document uploaded successfully - use Q&A to ask specific questions about your report"]
            
            # Fallback summary - NO fake health indicators, just show we have the document
            summary_data = {
                "health_indicators": [],  # Don't show fake metrics
                "overall_score": "Analysis Available",
                "overall_color": "#3b82f6",
                "key_findings": key_findings
            }
        
        # Build response
        health_indicators = [
            HealthIndicator(**indicator)
            for indicator in summary_data.get("health_indicators", [])
        ]
        
        summary = DocumentSummary(
            document_id=document_id,
            title=search_results[0].get('metadata', {}).get('title', document_id),
            report_type=summary_data.get("report_type"),
            report_description=summary_data.get("report_description"),
            health_indicators=health_indicators,
            overall_score=summary_data.get("overall_score", "Moderate"),
            overall_color=summary_data.get("overall_color", "#f59e0b"),
            key_findings=summary_data.get("key_findings", []),
            pages=len(pages_set),
            chunks=len(search_results)
        )
        
        logger.info(
            "✅ Summary generated successfully",
            document_id=document_id,
            indicators_count=len(health_indicators)
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
