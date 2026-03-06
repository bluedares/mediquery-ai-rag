"""
Synthesis Agent - Answer Generation with Citations
"""

import time
from app.agents.graph import AgentState
from app.utils.tracing import tracer
from app.utils.logger import logger
from app.services import bedrock_service
from app.config import settings

# Import Claude direct API service (used when USE_DIRECT_ANTHROPIC=true)
try:
    from app.services.claude import get_claude_service
    claude_available = True
except ImportError:
    claude_available = False


@tracer.trace_agent("SynthesisAgent")
async def synthesis_agent(state: AgentState) -> AgentState:
    """
    Generate final answer with citations using Claude Sonnet 4.6
    
    Responsibilities:
    1. Build context from reranked chunks
    2. Create prompt with instructions
    3. Call Claude Sonnet 4.6 for answer generation
    4. Extract citations and calculate confidence
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with final answer and citations
    """
    
    query = state['user_query']
    chunks = state['reranked_chunks']
    
    logger.debug(
        "✍️  Synthesizing answer",
        query=query,
        num_chunks=len(chunks),
        trace_id=state['request_id']
    )
    
    if not chunks:
        logger.warning(
            "⚠️  No chunks available for synthesis",
            trace_id=state['request_id']
        )
        state['final_answer'] = "I don't have enough information to answer this question."
        state['citations'] = []
        state['confidence'] = 0.0
        return state
    
    try:
        # Build context from chunks
        context_parts = []
        for i, chunk in enumerate(chunks):
            text = chunk.get('text', '')
            metadata = chunk.get('metadata', {})
            page = metadata.get('page', 'unknown')
            section = metadata.get('section', '')
            
            context_parts.append(
                f"[Source {i+1}] (Page {page}" + 
                (f", Section: {section}" if section else "") + 
                f")\n{text}"
            )
        
        context = "\n\n".join(context_parts)
        
        # Create system prompt
        system_prompt = """You are a friendly medical assistant helping patients understand their health reports.
Your role is to explain medical information in simple, easy-to-understand language.

Guidelines:
- Use SIMPLE language that anyone can understand
- Avoid complex medical jargon - explain in plain terms
- Keep answers SHORT and to the point (2-4 sentences max)
- Use line breaks to separate different points
- Cite sources using [Source N] format
- Be warm and reassuring in tone
- Answer ONLY based on the provided context"""
        
        # Create user prompt
        user_prompt = f"""Context from clinical document:

{context}

Question: {query}

Instructions:
1. Answer in SIMPLE, everyday language (avoid medical jargon)
2. Keep it SHORT - maximum 3-4 sentences
3. Use line breaks (\n\n) to separate different points for readability
4. Start with the most important finding first
5. Cite sources using [Source N] at the end of relevant sentences
6. If something is abnormal, explain what it means in simple terms
7. Answer ONLY from the context above

Answer:"""
        
        # Choose LLM service based on configuration
        if settings.use_direct_anthropic:
            # Use direct Anthropic API (temporary fallback)
            logger.warning(
                "⚠️  Using DIRECT Anthropic API (bypassing Bedrock security)",
                trace_id=state['request_id']
            )
            
            if not claude_available:
                raise Exception("Direct Anthropic API not available. Install anthropic package.")
            
            claude_service = get_claude_service()
            answer = await claude_service.invoke(
                prompt=user_prompt,
                max_tokens=settings.llm_max_tokens,
                temperature=settings.llm_temperature,
                top_p=settings.llm_top_p,
                trace_id=state['request_id'],
                system_prompt=system_prompt
            )
        else:
            # Use AWS Bedrock (production)
            logger.debug(
                "🧠 Calling Claude via Bedrock for synthesis",
                trace_id=state['request_id']
            )
            
            answer = await bedrock_service.invoke(
                prompt=user_prompt,
                max_tokens=settings.llm_max_tokens,
                temperature=settings.llm_temperature,
                top_p=settings.llm_top_p,
                trace_id=state['request_id'],
                system_prompt=system_prompt
            )
        
        # Build citations
        citations = []
        for i, chunk in enumerate(chunks):
            metadata = chunk.get('metadata', {})
            citations.append({
                'document_id': metadata.get('document_id', state['document_id']),
                'page': metadata.get('page', 0),
                'section': metadata.get('section'),
                'text': chunk.get('text', '')[:200],  # First 200 chars
                'relevance_score': state.get('rerank_scores', [])[i] if i < len(state.get('rerank_scores', [])) else 0.0
            })
        
        # Calculate confidence (simple heuristic based on scores)
        scores = state.get('rerank_scores', [])
        confidence = sum(scores) / len(scores) if scores else 0.5
        confidence = min(max(confidence, 0.0), 1.0)  # Clamp to [0, 1]
        
        # Update state
        state['final_answer'] = answer
        state['citations'] = citations
        state['confidence'] = confidence
        
        logger.info(
            "✅ Synthesis complete",
            answer_length=len(answer),
            num_citations=len(citations),
            confidence=round(confidence, 3),
            trace_id=state['request_id']
        )
        
        return state
        
    except Exception as e:
        logger.error(
            "❌ Synthesis failed",
            error=str(e),
            trace_id=state['request_id']
        )
        
        # Fallback answer
        state['final_answer'] = "I encountered an error while generating the answer. Please try again."
        state['citations'] = []
        state['confidence'] = 0.0
        
        if 'errors' not in state:
            state['errors'] = []
        state['errors'].append(f"Synthesis error: {str(e)}")
        
        return state
