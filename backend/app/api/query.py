"""
Query API - Document Question Answering
"""

from fastapi import APIRouter, HTTPException, status
import uuid
import time

from ..models.requests import QueryRequest
from ..models.responses import QueryResponse, Citation, AgentTraceEntry
from ..agents import agent_graph
from ..utils.logger import logger

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query_document(request: QueryRequest):
    """
    Query a document with natural language question
    
    This endpoint uses a multi-agent RAG system to:
    1. Analyze the query intent
    2. Retrieve relevant document chunks
    3. Rerank chunks by relevance
    4. Generate a cited answer using Claude Sonnet 4.6
    
    Args:
        request: Query request with query text and document ID
        
    Returns:
        QueryResponse with answer, citations, and agent trace
    """
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    logger.info(
        "📨 Query request received",
        request_id=request_id,
        query=request.query,
        document_id=request.document_id
    )
    
    try:
        # Initialize agent state
        initial_state = {
            'request_id': request_id,
            'user_query': request.query,
            'document_id': request.document_id,
            'conversation_id': request.conversation_id,
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
        
        logger.debug(
            "🚀 Starting agent workflow",
            request_id=request_id
        )
        
        # Execute agent graph
        result = await agent_graph.ainvoke(initial_state)
        
        # Calculate total processing time
        processing_time_ms = (time.time() - start_time) * 1000
        
        # Build citations
        citations = [
            Citation(
                document_id=cite['document_id'],
                page=cite['page'],
                section=cite.get('section'),
                text=cite['text'],
                relevance_score=cite['relevance_score']
            )
            for cite in result.get('citations', [])
        ]
        
        # Build agent trace if requested
        agent_trace = None
        if request.include_trace:
            agent_trace = [
                AgentTraceEntry(
                    agent=trace['agent'],
                    duration_ms=trace['duration_ms'],
                    status=trace['status'],
                    timestamp=trace['timestamp'],
                    input_summary=trace.get('input_summary'),
                    output_summary=trace.get('output_summary')
                )
                for trace in result.get('agent_trace', [])
            ]
        
        # Check for errors
        if result.get('errors'):
            logger.warning(
                "⚠️  Query completed with errors",
                request_id=request_id,
                errors=result['errors']
            )
        
        # Build response
        response = QueryResponse(
            request_id=request_id,
            answer=result.get('final_answer', 'No answer generated'),
            citations=citations,
            confidence=result.get('confidence', 0.0),
            processing_time_ms=processing_time_ms,
            agent_trace=agent_trace,
            metadata={
                'intent': result.get('intent'),
                'strategy': result.get('search_strategy'),
                'chunks_retrieved': len(result.get('retrieved_chunks', [])),
                'chunks_used': len(result.get('reranked_chunks', []))
            }
        )
        
        logger.info(
            "✅ Query completed successfully",
            request_id=request_id,
            processing_time_ms=round(processing_time_ms, 2),
            confidence=round(response.confidence, 3)
        )
        
        return response
        
    except Exception as e:
        logger.error(
            "❌ Query failed",
            request_id=request_id,
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Query processing failed",
                "message": str(e),
                "request_id": request_id
            }
        )
