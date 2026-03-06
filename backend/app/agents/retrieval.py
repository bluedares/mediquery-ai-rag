"""
Retrieval Agent - Document Chunk Retrieval
"""

import time
from typing import List, Dict
from app.agents.graph import AgentState
from app.utils.tracing import tracer
from app.utils.logger import logger
from app.services import opensearch_service, embedding_service
from app.config import settings

# Import ChromaDB service (used when USE_CHROMADB=true)
try:
    from app.services.chromadb_service import get_chromadb_service
    chromadb_available = True
except ImportError:
    chromadb_available = False


@tracer.trace_agent("RetrievalAgent")
async def retrieval_agent(state: AgentState) -> AgentState:
    """
    Retrieve relevant document chunks using vector search
    
    Responsibilities:
    1. Generate query embedding
    2. Perform vector/hybrid search in OpenSearch
    3. Return top-k most relevant chunks
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with retrieved chunks
    """
    
    query = state['user_query']
    document_id = state['document_id']
    strategy = state['search_strategy']
    
    logger.debug(
        "🔍 Retrieving chunks",
        query=query,
        document_id=document_id,
        strategy=strategy,
        trace_id=state['request_id']
    )
    
    try:
        # Generate query embedding
        logger.debug("Generating query embedding")
        query_embedding = await embedding_service.encode_single(query)
        
        # Determine collection/index name
        collection_name = f"medical-docs-{document_id}"
        
        # Choose vector database based on configuration
        if settings.use_chromadb:
            logger.debug("📊 Using ChromaDB for retrieval")
            if not chromadb_available:
                raise Exception("ChromaDB not available. Install chromadb package.")
            
            chromadb_svc = get_chromadb_service()
            
            # ChromaDB uses vector search (hybrid search is same as vector search)
            if strategy == 'semantic' or strategy == 'hybrid':
                chunks = await chromadb_svc.vector_search(
                    collection_name=collection_name,
                    query_embedding=query_embedding,
                    top_k=settings.top_k_retrieval
                )
            else:  # keyword
                chunks = await chromadb_svc.hybrid_search(
                    collection_name=collection_name,
                    query_text=query,
                    query_embedding=query_embedding,
                    top_k=settings.top_k_retrieval
                )
        else:
            logger.debug("📊 Using OpenSearch for retrieval")
            index_name = collection_name
            
            # Perform search based on strategy
            if strategy == 'semantic':
                # Pure vector search
                chunks = await opensearch_service.vector_search(
                    index_name=index_name,
                    query_embedding=query_embedding,
                    top_k=settings.top_k_retrieval
                )
            elif strategy == 'keyword':
                # TODO: Implement pure keyword search
                chunks = await opensearch_service.hybrid_search(
                    index_name=index_name,
                    query_text=query,
                    query_embedding=query_embedding,
                    top_k=settings.top_k_retrieval
                )
            else:  # hybrid
                # Hybrid search (semantic + keyword)
                chunks = await opensearch_service.hybrid_search(
                    index_name=index_name,
                    query_text=query,
                    query_embedding=query_embedding,
                    top_k=settings.top_k_retrieval
                )
        
        # Extract scores
        scores = [chunk.get('score', 0.0) for chunk in chunks]
        
        # Update state
        state['retrieved_chunks'] = chunks
        state['retrieval_scores'] = scores
        
        logger.info(
            "✅ Retrieval complete",
            chunks_retrieved=len(chunks),
            avg_score=round(sum(scores) / len(scores), 3) if scores else 0,
            trace_id=state['request_id']
        )
        
        return state
        
    except Exception as e:
        logger.error(
            "❌ Retrieval failed",
            error=str(e),
            trace_id=state['request_id']
        )
        
        # Add error to state
        if 'errors' not in state:
            state['errors'] = []
        state['errors'].append(f"Retrieval error: {str(e)}")
        
        # Return empty results
        state['retrieved_chunks'] = []
        state['retrieval_scores'] = []
        
        return state
