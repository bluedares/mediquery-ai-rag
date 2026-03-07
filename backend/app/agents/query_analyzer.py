"""
Query Analyzer Agent - Intent Classification and Strategy Selection
"""

import time
from .graph import AgentState
from ..utils.tracing import tracer
from ..utils.logger import logger


@tracer.trace_agent("QueryAnalyzerAgent")
async def query_analyzer_agent(state: AgentState) -> AgentState:
    """
    Analyze user query to determine intent and search strategy
    
    Responsibilities:
    1. Validate query is medical/report-related
    2. Classify query intent (factual, comparison, enumeration, etc.)
    3. Determine optimal search strategy (semantic, keyword, hybrid)
    4. Optionally expand query with synonyms
    
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
    
    # Validate query is medical/report-related
    query_lower = query.lower()
    
    # Medical/health-related keywords
    medical_keywords = [
        'test', 'result', 'report', 'value', 'level', 'count', 'blood', 'glucose', 
        'cholesterol', 'hemoglobin', 'platelet', 'wbc', 'rbc', 'pressure', 'heart',
        'kidney', 'liver', 'thyroid', 'diabetes', 'anemia', 'infection', 'disease',
        'normal', 'abnormal', 'high', 'low', 'range', 'reference', 'health', 'medical',
        'doctor', 'diagnosis', 'symptom', 'treatment', 'medication', 'lab', 'clinical',
        'patient', 'finding', 'analysis', 'interpretation', 'concern', 'risk', 'condition',
        'name', 'age', 'gender', 'date', 'hospital', 'clinic', 'physician'
    ]
    
    # Check if query contains any medical keywords
    is_medical = any(keyword in query_lower for keyword in medical_keywords)
    
    # If not medical-related, reject the query
    if not is_medical:
        logger.warning(
            "⚠️ Non-medical query detected",
            query=query,
            trace_id=state['request_id']
        )
        state['intent'] = 'non_medical'
        state['search_strategy'] = 'none'
        state['expanded_query'] = None
        state['final_answer'] = "I can only answer questions related to your medical report. Please ask about your test results, health values, or medical findings."
        state['citations'] = []
        state['confidence'] = 0.0
        # Skip retrieval and synthesis by setting empty chunks
        state['retrieved_chunks'] = []
        state['retrieval_scores'] = []
        state['reranked_chunks'] = []
        state['rerank_scores'] = []
        return state
    
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
    
    # Implement query expansion for better retrieval
    expanded_query = None
    query_lower = query.lower()
    
    # If asking about normal values, expand query to include reference range terms
    if any(term in query_lower for term in ['normal', 'abnormal', 'high', 'low', 'range', 'reference']):
        expanded_query = f"{query} reference range normal values reference interval"
        logger.debug(
            "🔍 Expanded query to include reference range terms",
            original=query,
            expanded=expanded_query,
            request_id=state['request_id']
        )
    
    # Update state
    state['intent'] = intent
    state['search_strategy'] = strategy
    state['expanded_query'] = expanded_query
    
    logger.info(
        "✅ Query analysis complete",
        intent=intent,
        strategy=strategy,
        trace_id=state['request_id']
    )
    
    return state
