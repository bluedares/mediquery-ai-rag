"""
Query Analyzer Agent - Intent Classification and Strategy Selection
"""

import time
from app.agents.graph import AgentState
from app.utils.tracing import tracer
from app.utils.logger import logger


@tracer.trace_agent("QueryAnalyzerAgent")
async def query_analyzer_agent(state: AgentState) -> AgentState:
    """
    Analyze user query to determine intent and search strategy
    
    Responsibilities:
    1. Classify query intent (factual, comparison, enumeration, etc.)
    2. Determine optimal search strategy (semantic, keyword, hybrid)
    3. Optionally expand query with synonyms
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with intent and strategy
    """
    
    query = state['user_query']
    
    logger.debug(
        "🔍 Analyzing query",
        query=query,
        query_length=len(query),
        trace_id=state['request_id']
    )
    
    # Intent classification (rule-based for now, can use LLM for complex cases)
    query_lower = query.lower()
    
    # Factual lookup
    if any(word in query_lower for word in ['what', 'define', 'explain', 'describe']):
        intent = 'factual_lookup'
        strategy = 'hybrid'
        logger.debug("Intent: Factual lookup")
    
    # Comparison
    elif any(word in query_lower for word in ['compare', 'difference', 'versus', 'vs', 'better']):
        intent = 'comparison'
        strategy = 'semantic'
        logger.debug("Intent: Comparison")
    
    # Enumeration
    elif any(word in query_lower for word in ['list', 'enumerate', 'all', 'how many']):
        intent = 'enumeration'
        strategy = 'keyword'
        logger.debug("Intent: Enumeration")
    
    # Analytical
    elif any(word in query_lower for word in ['why', 'how', 'analyze', 'reason']):
        intent = 'analytical'
        strategy = 'hybrid'
        logger.debug("Intent: Analytical")
    
    # Default
    else:
        intent = 'general_query'
        strategy = 'hybrid'
        logger.debug("Intent: General query")
    
    # Update state
    state['intent'] = intent
    state['search_strategy'] = strategy
    state['expanded_query'] = None  # TODO: Implement query expansion
    
    logger.info(
        "✅ Query analysis complete",
        intent=intent,
        strategy=strategy,
        trace_id=state['request_id']
    )
    
    return state
