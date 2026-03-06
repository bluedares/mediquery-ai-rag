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
        # Implement smart reranking that prioritizes chunks with test results
        import re
        
        def has_numerical_values(text: str) -> bool:
            """Check if chunk contains numerical test values"""
            # Look for patterns like "12.5 g/dL", "5.4%", "18 ng/mL", etc.
            number_pattern = r'\d+\.?\d*\s*(?:g/dL|mg/dL|ng/mL|%|mmol/L|U/L|IU/L)'
            return bool(re.search(number_pattern, text))
        
        # Score chunks based on retrieval score + bonus for numerical values
        scored_chunks = []
        retrieval_scores = state.get('retrieval_scores', [])
        
        for i, chunk in enumerate(chunks):
            base_score = retrieval_scores[i] if i < len(retrieval_scores) else 0.5
            text = chunk.get('text', '')
            
            # Boost score if chunk contains numerical test values
            if has_numerical_values(text):
                boosted_score = base_score * 1.3  # 30% boost for chunks with test values
                logger.debug(f"Boosted chunk {i} score from {base_score:.3f} to {boosted_score:.3f} (contains test values)")
            else:
                boosted_score = base_score
            
            scored_chunks.append((chunk, boosted_score))
        
        # Sort by boosted score
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        
        # Select more chunks to ensure we get test results
        top_k = min(15, len(scored_chunks))  # Increased from 5 to 15
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
