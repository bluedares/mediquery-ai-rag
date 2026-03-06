"""
LLM Call Tracer with Cost Estimation
"""

from typing import Optional
from app.config import settings
from app.utils.logger import logger


class LLMTracer:
    """
    Trace LLM API calls with detailed metrics and cost estimation
    
    Features:
    - Token counting
    - Cost estimation
    - Prompt/response logging
    - Performance metrics
    - Model-specific pricing
    """
    
    # Pricing per 1K tokens (as of Feb 2026)
    PRICING = {
        "claude-sonnet-4-6": {
            "input": 0.003,   # $3 per 1M input tokens
            "output": 0.015   # $15 per 1M output tokens
        },
        "claude-3-5-sonnet": {
            "input": 0.003,
            "output": 0.015
        },
        "claude-3-opus": {
            "input": 0.015,
            "output": 0.075
        },
        "claude-3-haiku": {
            "input": 0.00025,
            "output": 0.00125
        },
        "default": {
            "input": 0.003,
            "output": 0.015
        }
    }
    
    @staticmethod
    async def trace_llm_call(
        model_id: str,
        prompt: str,
        response: str,
        tokens_input: int,
        tokens_output: int,
        duration_ms: float,
        trace_id: str,
        metadata: Optional[dict] = None
    ):
        """
        Log LLM call with detailed metrics
        
        Args:
            model_id: Model identifier
            prompt: Input prompt
            response: Model response
            tokens_input: Number of input tokens
            tokens_output: Number of output tokens
            duration_ms: Call duration in milliseconds
            trace_id: Request trace ID
            metadata: Additional metadata
        """
        
        # Calculate cost
        cost = LLMTracer._estimate_cost(model_id, tokens_input, tokens_output)
        
        # Total tokens
        total_tokens = tokens_input + tokens_output
        
        # Log LLM call summary
        if settings.trace_llm_calls:
            logger.info(
                "🧠 LLM Call - Claude Sonnet 4.6",
                model=model_id,
                trace_id=trace_id,
                tokens_input=tokens_input,
                tokens_output=tokens_output,
                total_tokens=total_tokens,
                duration_ms=round(duration_ms, 2),
                cost_usd=cost,
                tokens_per_second=round(total_tokens / (duration_ms / 1000), 2) if duration_ms > 0 else 0,
                **(metadata or {})
            )
        
        # Log prompt
        if settings.trace_llm_prompts:
            prompt_preview = prompt[:500] + "..." if len(prompt) > 500 else prompt
            logger.debug(
                "📝 LLM Prompt",
                model=model_id,
                trace_id=trace_id,
                prompt=prompt_preview,
                prompt_length=len(prompt),
                prompt_tokens=tokens_input
            )
        
        # Log response
        if settings.trace_llm_responses:
            response_preview = response[:500] + "..." if len(response) > 500 else response
            logger.debug(
                "💬 LLM Response",
                model=model_id,
                trace_id=trace_id,
                response=response_preview,
                response_length=len(response),
                response_tokens=tokens_output
            )
        
        # Log cost if enabled
        if settings.trace_llm_cost:
            logger.debug(
                "💰 LLM Cost",
                model=model_id,
                trace_id=trace_id,
                cost_usd=cost,
                tokens_input=tokens_input,
                tokens_output=tokens_output,
                cost_per_1k_input=LLMTracer._get_pricing(model_id)["input"],
                cost_per_1k_output=LLMTracer._get_pricing(model_id)["output"]
            )
    
    @staticmethod
    def _estimate_cost(model_id: str, tokens_input: int, tokens_output: int) -> float:
        """
        Estimate cost for LLM call
        
        Args:
            model_id: Model identifier
            tokens_input: Number of input tokens
            tokens_output: Number of output tokens
            
        Returns:
            Estimated cost in USD
        """
        pricing = LLMTracer._get_pricing(model_id)
        
        cost_input = (tokens_input / 1000) * pricing["input"]
        cost_output = (tokens_output / 1000) * pricing["output"]
        
        total_cost = cost_input + cost_output
        
        return round(total_cost, 6)
    
    @staticmethod
    def _get_pricing(model_id: str) -> dict:
        """
        Get pricing for model
        
        Args:
            model_id: Model identifier
            
        Returns:
            Pricing dictionary with input/output rates
        """
        # Extract model name from ID
        model_name = model_id.lower()
        
        # Check for specific models
        for key in LLMTracer.PRICING:
            if key in model_name:
                return LLMTracer.PRICING[key]
        
        # Return default pricing
        return LLMTracer.PRICING["default"]
    
    @staticmethod
    def estimate_tokens(text: str) -> int:
        """
        Estimate token count for text (rough approximation)
        
        Args:
            text: Input text
            
        Returns:
            Estimated token count
        """
        # Rough approximation: 1 token ≈ 4 characters
        return len(text) // 4


# Global LLM tracer instance
llm_tracer = LLMTracer()
