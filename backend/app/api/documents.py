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
        prompt = f"""Extract medical test results from this report.

Medical Report:
{full_text[:4000]}

IMPORTANT - Extract ONLY actual medical test results, NOT metadata:
- YES: Hemoglobin, Glucose, WBC, Cholesterol, TSH, Creatinine, etc.
- NO: Run Number, Rack ID, Sample ID, Report Date, Analysis Performed, etc.

Task:
1. Find medical test results with numeric values (blood tests, urine tests, vitals, etc.)
2. SKIP metadata fields like: run number, rack ID, tube number, sample ID, dates, times, report codes
3. For each MEDICAL test:
   - name: actual test name (e.g., "Hemoglobin", "Glucose")
   - value: numeric result
   - status: compare to reference range if provided
     * Below range or "L" → "needs attention", "#ef4444"
     * Above range or "H" → "needs attention", "#ef4444"
     * Borderline → "moderate", "#f59e0b"
     * Normal → "good", "#10b981"

4. Overall score based on worst test result

Return JSON with ONLY medical test results:

{{
    "report_type": "Blood Test",
    "report_description": "Complete blood count analysis",
    "health_indicators": [
        {{"name": "Hemoglobin", "value": 12.5, "status": "needs attention", "color": "#ef4444"}},
        {{"name": "WBC Count", "value": 8000, "status": "good", "color": "#10b981"}}
    ],
    "overall_score": "Needs Attention",
    "overall_color": "#ef4444",
    "key_findings": ["Low hemoglobin detected", "WBC count normal"]
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
            indicators_count = len(summary_data.get('health_indicators', []))
            logger.info(f"✅ Successfully parsed LLM response with {indicators_count} indicators")
            
            # If LLM returned empty indicators, treat as parsing failure and use fallback
            if indicators_count == 0:
                logger.warning("LLM returned empty health_indicators array, using fallback extraction")
                raise ValueError("Empty health_indicators from LLM")
        except Exception as e:
            logger.warning(f"Failed to parse LLM response: {e}")
            logger.warning(f"Response was: {response[:500]}")
            
            # Extract test results from document text as fallback
            import re
            key_findings = []
            health_indicators = []
            
            # Try to extract test results from various medical report formats
            for result in search_results[:20]:
                text = result.get('text', '').strip()
                if not text:
                    continue
                
                # Look for various test result patterns across different medical report types
                test_patterns = [
                    # Pattern: "Test Name: 84.4" or "Test Name = 84.4"
                    r'([A-Za-z][A-Za-z0-9\s\(\)]+?)\s*[:=]\s*([LH]?\s*[\d.]+)\s*(%|g/dL|mg/dL|mmol/L|U/L|cells/cumm|mm|cm|kg|lbs|bpm|mmHg)?',
                    # Pattern: "Test Name 84.4 unit"
                    r'([A-Za-z][A-Za-z0-9\s\(\)]+?)\s+([\d.]+)\s*(%|g/dL|mg/dL|mmol/L|U/L|cells/cumm|mm|cm|kg|lbs|bpm|mmHg)',
                    # Pattern: "Test Name\nResult: 84.4"
                    r'([A-Za-z][A-Za-z0-9\s\(\)]+?)\s*\n\s*(?:Result|Value)?\s*[:=]?\s*([\d.]+)',
                ]
                
                for pattern in test_patterns:
                    matches = re.finditer(pattern, text, re.IGNORECASE)
                    for match in matches:
                        test_name = match.group(1).strip()
                        test_value = match.group(2).strip()
                        
                        # Comprehensive metadata exclusion list
                        metadata_keywords = [
                            'page', 'ref', 'id', 'age', 'sex', 'date', 'time', 'number', 'code',
                            'analysis', 'performed', 'run', 'rack', 'tube', 'report', 'generated',
                            'sample', 'specimen', 'barcode', 'patient', 'doctor', 'lab', 'laboratory',
                            'version', 'batch', 'serial', 'accession', 'order', 'requisition',
                            'printed', 'collected', 'received', 'registered', 'verified'
                        ]
                        
                        # Skip if test name is too short or contains metadata keywords
                        test_name_lower = test_name.lower()
                        if len(test_name) < 3:
                            continue
                        
                        # Check if test name contains any metadata keywords
                        if any(keyword in test_name_lower for keyword in metadata_keywords):
                            continue
                        
                        # Skip if test name is mostly numbers (likely an ID)
                        if sum(c.isdigit() for c in test_name) > len(test_name) / 2:
                            continue
                        
                        # Try to convert value to number and detect abnormal markers
                        try:
                            # Check for L (Low) or H (High) markers
                            is_low = 'L' in test_value and test_value.index('L') < 3
                            is_high = 'H' in test_value and test_value.index('H') < 3
                            
                            value_num = float(test_value.replace('L', '').replace('H', '').strip())
                            if 0 < value_num < 1000:  # Reasonable range
                                # Determine status based on L/H markers
                                if is_low or is_high:
                                    status = "needs attention"
                                    color = "#ef4444"
                                else:
                                    status = "good"
                                    color = "#10b981"
                                
                                health_indicators.append({
                                    "name": test_name[:30],  # Limit length
                                    "value": round(value_num, 1),
                                    "status": status,
                                    "color": color
                                })
                        except:
                            continue
                
                # Extract meaningful sentences for key findings
                sentences = text.split('.')
                for sentence in sentences:
                    sentence = sentence.strip()
                    if 40 <= len(sentence) <= 200:
                        if re.search(r'\b(test|result|level|count|shows|indicates|negative|positive|normal|abnormal)\b', sentence, re.I):
                            if sentence not in key_findings:
                                key_findings.append(sentence)
                
                if len(health_indicators) >= 5 and len(key_findings) >= 3:
                    break
            
            # Remove duplicates from health indicators
            seen_names = set()
            unique_indicators = []
            for ind in health_indicators:
                if ind['name'] not in seen_names:
                    seen_names.add(ind['name'])
                    unique_indicators.append(ind)
            
            # If still no findings, use generic message
            if not key_findings:
                key_findings = ["Medical report uploaded successfully", "Use Q&A below to ask specific questions about your test results"]
            
            # Determine overall score based on extracted indicators
            overall_score = "Good"
            overall_color = "#10b981"
            
            if unique_indicators:
                # Check if any indicators have concerning status
                has_red = any(ind.get('color') == '#ef4444' for ind in unique_indicators)
                has_yellow = any(ind.get('color') == '#f59e0b' for ind in unique_indicators)
                
                if has_red:
                    overall_score = "Needs Attention"
                    overall_color = "#ef4444"
                elif has_yellow:
                    overall_score = "Moderate"
                    overall_color = "#f59e0b"
            else:
                # No indicators extracted - neutral status
                overall_score = "Moderate"
                overall_color = "#3b82f6"
            
            # Fallback summary with extracted data
            summary_data = {
                "report_type": "Medical Test Report",
                "report_description": "Laboratory test results and medical analysis",
                "health_indicators": unique_indicators[:10],  # Limit to 10
                "overall_score": overall_score,
                "overall_color": overall_color,
                "key_findings": key_findings[:5]  # Limit to 5
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
