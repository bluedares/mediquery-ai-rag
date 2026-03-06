"""
Reranking Agent - Cross-Encoder Reranking
"""

import time
from typing import List, Tuple
from app.agents.graph import AgentState
from app.utils.tracing import tracer
from app.utils.logger import logger
from app.config import settings


@tracer.trace_agent("RerankingAgent")
async def reranking_agent(state: AgentState) -> AgentState:
    """
    Rerank retrieved chunks using cross-encoder for better relevance
    
    Responsibilities:
    1. Score query-chunk pairs using cross-encoder
    2. Sort chunks by relevance score
    3. Select top-k chunks for synthesis
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with reranked chunks
    """
    
    query = state['user_query']
    chunks = state['retrieved_chunks']
    
    logger.debug(
        "🎯 Reranking chunks",
        query=query,
        num_chunks=len(chunks),
        trace_id=state['request_id']
    )
    
    if not chunks:
        logger.warning(
            "⚠️  No chunks to rerank",
            trace_id=state['request_id']
        )
        state['reranked_chunks'] = []
        state['rerank_scores'] = []
        return state
    
    try:
        # TODO: Implement actual cross-encoder reranking
        # For now, use simple heuristic based on retrieval scores
        
        # Sort by retrieval score (already have scores from retrieval)
        scored_chunks = list(zip(chunks, state.get('retrieval_scores', [])))
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        
        # Select top-k
        top_k = min(settings.top_k_rerank, len(scored_chunks))
        reranked = scored_chunks[:top_k]
        
        # Extract chunks and scores
        reranked_chunks = [chunk for chunk, _ in reranked]
        rerank_scores = [score for _, score in reranked]
        
        # Update state
        state['reranked_chunks'] = reranked_chunks
        state['rerank_scores'] = rerank_scores
        
        logger.info(
            "✅ Reranking complete",
            chunks_selected=len(reranked_chunks),
            avg_score=round(sum(rerank_scores) / len(rerank_scores), 3) if rerank_scores else 0,
            trace_id=state['request_id']
        )
        
        return state
        
    except Exception as e:
        logger.error(
            "❌ Reranking failed",
            error=str(e),
            trace_id=state['request_id']
        )
        
        # Fallback: use original chunks
        state['reranked_chunks'] = chunks[:settings.top_k_rerank]
        state['rerank_scores'] = state.get('retrieval_scores', [])[:settings.top_k_rerank]
        
        return state
