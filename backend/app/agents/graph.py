"""
LangGraph Multi-Agent System - State Graph Definition
"""

from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Annotated, Optional
from operator import add


class AgentState(TypedDict):
    """
    Shared state across all agents in the workflow
    
    This state is passed between agents and accumulates information
    as the workflow progresses.
    """
    # Request metadata
    request_id: str
    
    # User input
    user_query: str
    document_id: str
    conversation_id: Optional[str]
    
    # Query analysis
    intent: str
    search_strategy: str
    expanded_query: Optional[str]
    
    # Retrieval
    retrieved_chunks: List[Dict]
    retrieval_scores: List[float]
    
    # Reranking
    reranked_chunks: List[Dict]
    rerank_scores: List[float]
    
    # Synthesis
    final_answer: str
    citations: List[Dict]
    confidence: float
    
    # Tracing (accumulated across agents)
    agent_trace: Annotated[List[Dict], add]
    
    # Errors
    errors: List[str]


def create_agent_graph():
    """
    Create the LangGraph workflow for multi-agent RAG
    
    Workflow:
    1. QueryAnalyzerAgent - Analyze intent and strategy
    2. RetrievalAgent - Retrieve relevant chunks
    3. RerankingAgent - Rerank chunks by relevance
    4. SynthesisAgent - Generate final answer with citations
    
    Returns:
        Compiled StateGraph
    """
    from .query_analyzer import query_analyzer_agent
    from .retrieval import retrieval_agent
    from .reranking import reranking_agent
    from .synthesis import synthesis_agent
    
    # Create graph
    graph = StateGraph(AgentState)
    
    # Add agent nodes
    graph.add_node("query_analyzer", query_analyzer_agent)
    graph.add_node("retrieval", retrieval_agent)
    graph.add_node("reranking", reranking_agent)
    graph.add_node("synthesis", synthesis_agent)
    
    # Define workflow edges
    graph.set_entry_point("query_analyzer")
    graph.add_edge("query_analyzer", "retrieval")
    graph.add_edge("retrieval", "reranking")
    graph.add_edge("reranking", "synthesis")
    graph.add_edge("synthesis", END)
    
    # Compile graph
    return graph.compile()


# Global agent graph instance
agent_graph = create_agent_graph()
