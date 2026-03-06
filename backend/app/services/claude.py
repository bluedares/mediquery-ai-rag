"""
Anthropic Claude Direct API Service
TEMPORARY: Used as fallback while AWS Bedrock Marketplace subscription is pending
WARNING: This bypasses Bedrock security guarantees. Use only for demo/development.
"""

import anthropic
from typing import Optional
from app.config import settings
from app.utils.logger import logger
from app.utils.llm_tracer import llm_tracer


class ClaudeService:
    """
    Direct Anthropic API service for Claude models
    
    SECURITY NOTE: This service sends data directly to Anthropic's servers,
    bypassing AWS Bedrock's data isolation and privacy guarantees.
    Use only as temporary fallback during AWS Marketplace subscription setup.
    
    Features:
    - Direct API access to Claude models
    - Synchronous invocation
    - Token counting and cost tracking
    - Error handling
    - Comprehensive logging
    """
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize Claude direct API service
        
        Args:
            api_key: Anthropic API key (defaults to settings)
            model: Claude model name (defaults to settings)
        """
        self.api_key = api_key or settings.anthropic_api_key
        self.model = model or settings.anthropic_model
        
        if not self.api_key:
            raise ValueError("Anthropic API key is required. Set ANTHROPIC_API_KEY in .env")
        
        try:
            logger.warning(
                "⚠️  Initializing DIRECT Anthropic API (bypassing Bedrock security)",
                model=self.model,
                security_note="Data will be sent directly to Anthropic servers"
            )
            
            self.client = anthropic.Anthropic(api_key=self.api_key)
            
            logger.info(
                "✅ Claude direct API service initialized",
                model=self.model,
                api_version="2023-06-01"
            )
        except Exception as e:
            logger.error(
                "❌ Failed to initialize Claude direct API client",
                error=str(e),
                error_type=type(e).__name__
            )
            raise
    
    async def invoke(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.1,
        top_p: float = 0.9,
        trace_id: Optional[str] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Invoke Claude model with a prompt
        
        Args:
            prompt: User prompt/question
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-1.0)
            top_p: Nucleus sampling parameter
            trace_id: Request trace ID for logging
            system_prompt: Optional system prompt
            
        Returns:
            Generated text response
            
        Raises:
            Exception: If API call fails
        """
        try:
            logger.debug(
                "🤖 Calling Claude direct API",
                model=self.model,
                prompt_length=len(prompt),
                max_tokens=max_tokens,
                trace_id=trace_id
            )
            
            # Prepare messages
            messages = [{"role": "user", "content": prompt}]
            
            # Call Anthropic API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                system=system_prompt if system_prompt else anthropic.NOT_GIVEN,
                messages=messages
            )
            
            # Extract answer
            answer = response.content[0].text
            
            # Log usage
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            
            logger.info(
                "✅ Claude API response received",
                model=self.model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens,
                response_length=len(answer),
                trace_id=trace_id
            )
            
            # Trace LLM call
            await llm_tracer.trace_llm_call(
                model_id=f"anthropic-direct/{self.model}",
                prompt=prompt,
                response=answer,
                tokens_input=input_tokens,
                tokens_output=output_tokens,
                duration_ms=0,
                trace_id=trace_id or "unknown"
            )
            
            return answer
            
        except anthropic.OverloadedError as e:
            logger.warning(
                "⚠️  Anthropic API temporarily overloaded - retrying recommended",
                error_message=str(e),
                trace_id=trace_id
            )
            raise Exception("Anthropic API is temporarily overloaded. Please wait a few seconds and try again.")
        except anthropic.APIError as e:
            logger.error(
                "❌ Anthropic API error",
                error_message=str(e),
                error_type=type(e).__name__,
                status_code=getattr(e, 'status_code', None),
                trace_id=trace_id
            )
            raise Exception(f"Anthropic API error: {str(e)}")
            
        except Exception as e:
            logger.error(
                "❌ Unexpected error calling Claude API",
                error=str(e),
                error_type=type(e).__name__,
                trace_id=trace_id
            )
            raise Exception(f"Claude API error: {str(e)}")


# Global service instance (initialized on first import)
claude_service: Optional[ClaudeService] = None


def get_claude_service() -> ClaudeService:
    """Get or create Claude service instance"""
    global claude_service
    
    if claude_service is None:
        if settings.use_direct_anthropic:
            claude_service = ClaudeService()
        else:
            raise RuntimeError("Direct Anthropic API not enabled. Set USE_DIRECT_ANTHROPIC=true in .env")
    
    return claude_service
