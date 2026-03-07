"""
Amazon Bedrock Service - Claude Sonnet 4.6 Integration
"""

import boto3
import json
import time
from typing import AsyncGenerator, Optional, Dict, Any
from botocore.exceptions import ClientError

from ..config import settings
from ..utils.logger import logger
from ..utils.llm_tracer import llm_tracer


class BedrockService:
    """
    Amazon Bedrock service for Claude Sonnet 4.6 LLM inference
    
    Features:
    - Synchronous and streaming responses
    - Automatic token counting
    - Cost tracking
    - Error handling with retries
    - Comprehensive logging
    """
    
    def __init__(self, model_id: Optional[str] = None, region: Optional[str] = None):
        """
        Initialize Bedrock service
        
        Args:
            model_id: Claude model ID (defaults to settings)
            region: AWS region (defaults to settings)
        """
        self.model_id = model_id or settings.bedrock_model_id
        self.region = region or settings.aws_region
        
        # Initialize boto3 client
        try:
            logger.info(
                "🔧 Initializing Bedrock client",
                model_id=self.model_id,
                region=self.region,
                has_access_key=bool(settings.aws_access_key_id),
                has_secret_key=bool(settings.aws_secret_access_key)
            )
            
            logger.debug(
                "🔧 Bedrock client initialization details",
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
                region_name=self.region
            )
            
            self.client = boto3.client(
                'bedrock-runtime',
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
                region_name=self.region
            )
            
            logger.info(
                "✅ Bedrock service initialized successfully",
                model_id=self.model_id,
                region=self.region
            )
        except Exception as e:
            logger.error(
                "❌ Failed to initialize Bedrock client",
                error=str(e),
                region=self.region,
                error_type=type(e).__name__,
                error_traceback=e.__traceback__
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
        Invoke Claude Sonnet 4.6 model synchronously
        
        Args:
            prompt: User prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)
            top_p: Nucleus sampling parameter
            trace_id: Request trace ID for logging
            system_prompt: Optional system prompt
            
        Returns:
            Generated text response
        """
        start_time = time.time()
        
        logger.debug(
            "🧠 Invoking Bedrock",
            model=self.model_id,
            prompt_length=len(prompt),
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        # Build request body
        messages = [{"role": "user", "content": prompt}]
        
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p
        }
        
        # Add system prompt if provided
        if system_prompt:
            body["system"] = system_prompt
        
        try:
            # Invoke model
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body)
            )
            
            # Parse response
            result = json.loads(response['body'].read())
            answer = result['content'][0]['text']
            
            # Extract usage metrics
            usage = result.get('usage', {})
            tokens_input = usage.get('input_tokens', len(prompt) // 4)
            tokens_output = usage.get('output_tokens', len(answer) // 4)
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Trace LLM call
            await llm_tracer.trace_llm_call(
                model_id=self.model_id,
                prompt=prompt,
                response=answer,
                tokens_input=tokens_input,
                tokens_output=tokens_output,
                duration_ms=duration_ms,
                trace_id=trace_id or "unknown",
                metadata={
                    "temperature": temperature,
                    "top_p": top_p,
                    "max_tokens": max_tokens
                }
            )
            
            return answer
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            # Comprehensive error logging with specific categorization
            logger.error(
                "❌ Bedrock API error - Detailed diagnostics",
                model_id=self.model_id,
                error_code=error_code,
                error_message=error_message,
                region=self.region,
                error_type=type(e).__name__,
                request_id=e.response.get('ResponseMetadata', {}).get('RequestId', 'N/A'),
                http_status_code=e.response.get('ResponseMetadata', {}).get('HTTPStatusCode', 'N/A')
            )
            
            # Handle specific error types with detailed logging
            if error_code == 'AccessDeniedException':
                if 'INVALID_PAYMENT_INSTRUMENT' in error_message:
                    logger.error(
                        "💳 PAYMENT ERROR: Invalid or missing payment method",
                        action_required="Add valid payment method in AWS Console → Billing → Payment methods",
                        error_details=error_message
                    )
                    raise Exception(f"Payment required: {error_message}")
                else:
                    logger.error(
                        "🔒 ACCESS DENIED: Model access not enabled",
                        action_required=f"Enable model access in AWS Console → Bedrock → Model Access",
                        model_id=self.model_id,
                        error_details=error_message
                    )
                    raise Exception(f"Access denied: {error_message}")
            
            elif error_code == 'ThrottlingException':
                logger.error(
                    "⏱️ RATE LIMIT: Too many requests",
                    action_required="Wait and retry, or request quota increase",
                    error_details=error_message
                )
                raise Exception("Rate limit exceeded. Please retry later.")
            
            elif error_code == 'ValidationException':
                logger.error(
                    "⚠️ VALIDATION ERROR: Invalid request parameters",
                    model_id=self.model_id,
                    error_details=error_message,
                    possible_causes="Invalid model ID, unsupported parameters, or malformed request"
                )
                raise Exception(f"Invalid request: {error_message}")
            
            elif error_code == 'ResourceNotFoundException':
                logger.error(
                    "🔍 RESOURCE NOT FOUND: Model or resource unavailable",
                    model_id=self.model_id,
                    error_details=error_message,
                    action_required="Verify model ID is correct and available in your region"
                )
                raise Exception(f"Resource not found: {error_message}")
            
            elif error_code == 'ServiceUnavailableException':
                logger.error(
                    "🔧 SERVICE UNAVAILABLE: Temporary AWS service issue",
                    error_details=error_message,
                    action_required="Retry after a few seconds"
                )
                raise Exception(f"Service unavailable: {error_message}")
            
            else:
                logger.error(
                    "❓ UNKNOWN BEDROCK ERROR",
                    error_code=error_code,
                    error_message=error_message,
                    full_response=str(e.response)
                )
                raise Exception(f"Bedrock error [{error_code}]: {error_message}")
        
        except Exception as e:
            logger.error(
                "❌ UNEXPECTED ERROR calling Bedrock",
                error=str(e),
                error_type=type(e).__name__,
                model_id=self.model_id,
                prompt_length=len(prompt),
                max_tokens=max_tokens,
                temperature=temperature
            )
            import traceback
            logger.error(
                "📋 Full traceback",
                traceback=traceback.format_exc()
            )
            raise
    
    async def stream(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.1,
        top_p: float = 0.9,
        system_prompt: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream Claude Sonnet 4.6 responses
        
        Args:
            prompt: User prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            system_prompt: Optional system prompt
            
        Yields:
            Text chunks as they are generated
        """
        logger.debug(
            "🌊 Streaming from Bedrock",
            model=self.model_id,
            prompt_length=len(prompt)
        )
        
        # Build request body
        messages = [{"role": "user", "content": prompt}]
        
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p
        }
        
        if system_prompt:
            body["system"] = system_prompt
        
        try:
            # Invoke with streaming
            response = self.client.invoke_model_with_response_stream(
                modelId=self.model_id,
                body=json.dumps(body)
            )
            
            # Stream chunks
            for event in response['body']:
                chunk = json.loads(event['chunk']['bytes'])
                
                if chunk['type'] == 'content_block_delta':
                    if 'delta' in chunk and 'text' in chunk['delta']:
                        yield chunk['delta']['text']
                
                elif chunk['type'] == 'message_stop':
                    logger.debug("🏁 Streaming complete")
                    break
        
        except Exception as e:
            logger.error(
                "❌ Error streaming from Bedrock",
                error=str(e),
                error_type=type(e).__name__
            )
            raise
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text
        
        Args:
            text: Input text
            
        Returns:
            Estimated token count
        """
        # Rough approximation: 1 token ≈ 4 characters
        return len(text) // 4
    
    async def health_check(self) -> bool:
        """
        Check if Bedrock service is available
        
        Returns:
            True if service is healthy
        """
        try:
            # Simple test invocation
            await self.invoke(
                prompt="Test",
                max_tokens=10,
                trace_id="health_check"
            )
            return True
        except Exception as e:
            logger.warning(
                "⚠️  Bedrock health check failed",
                error=str(e)
            )
            return False


# Global service instance
bedrock_service = BedrockService()
