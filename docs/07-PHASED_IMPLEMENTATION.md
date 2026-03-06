# Phased Implementation Guide - MediQuery AI

## 🎯 Implementation Phases with Debug System

This document provides a detailed, phase-by-phase implementation guide with Claude Sonnet 4.6 and comprehensive debug/tracing capabilities.

---

## 📅 Timeline Overview

| Phase | Duration | Focus | Status |
|-------|----------|-------|--------|
| **Phase 0** | 2 hours | Debug Infrastructure | 🔄 Ready |
| **Phase 1** | 4 hours | Project Setup | 🔄 Ready |
| **Phase 2** | 12 hours | Backend + Agents | 🔄 Ready |
| **Phase 3** | 8 hours | Frontend | 🔄 Ready |
| **Phase 4** | 8 hours | AWS Deployment | 🔄 Ready |
| **Phase 5** | 4 hours | Testing & Demo | 🔄 Ready |
| **Total** | **38 hours** | 6-7 days | |

---

## 🔧 Phase 0: Debug Infrastructure Setup (2 hours)

### **Objectives**
- Set up global debug configuration
- Implement structured logging
- Create agent tracer decorator
- Add LLM call tracing
- Enable AWS X-Ray integration

### **Deliverables**

#### 0.1 Debug Configuration
**File**: `backend/app/config.py`

```python
from pydantic_settings import BaseSettings
from enum import Enum

class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"

class Settings(BaseSettings):
    # AWS Configuration
    aws_region: str = "us-east-1"
    s3_bucket: str
    opensearch_endpoint: str
    bedrock_model_id: str = "anthropic.claude-sonnet-4-6-20260223-v1:0"
    
    # Debug Configuration
    debug_mode: bool = True
    log_level: LogLevel = LogLevel.DEBUG
    log_format: str = "json"  # json or console
    
    # Agent Tracing
    trace_agents: bool = True
    trace_agent_inputs: bool = True
    trace_agent_outputs: bool = True
    trace_agent_timing: bool = True
    
    # LLM Tracing
    trace_llm_calls: bool = True
    trace_llm_prompts: bool = True
    trace_llm_responses: bool = True
    trace_llm_tokens: bool = True
    
    # Performance
    slow_query_threshold_ms: int = 3000
    
    # Distributed Tracing
    enable_xray: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()
```

#### 0.2 Structured Logging
**File**: `backend/app/utils/logger.py`

```python
import structlog
import logging
import sys
from pathlib import Path
from app.config import settings

def setup_logging():
    """Configure structured logging with emoji indicators"""
    
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if settings.log_format == "json"
            else structlog.dev.ConsoleRenderer(colors=True)
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(settings.log_level)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if settings.debug_mode else logging.INFO)
    logging.root.addHandler(console_handler)
    
    # File handler
    file_handler = logging.FileHandler("logs/mediquery.log")
    file_handler.setLevel(logging.DEBUG)
    logging.root.addHandler(file_handler)
    
    return structlog.get_logger()

logger = setup_logging()
```

#### 0.3 Agent Tracer
**File**: `backend/app/utils/tracing.py`

```python
import time
import functools
import uuid
from typing import Any, Callable
from app.utils.logger import logger
from app.config import settings

class AgentTracer:
    """Comprehensive agent execution tracer"""
    
    def trace_agent(self, agent_name: str):
        """Decorator to trace agent execution with detailed logging"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            async def wrapper(state: dict, *args, **kwargs) -> dict:
                trace_id = state.get('request_id', str(uuid.uuid4()))
                start_time = time.time()
                
                # Agent start
                if settings.trace_agents:
                    logger.info(
                        f"🤖 Agent Started: {agent_name}",
                        agent=agent_name,
                        trace_id=trace_id,
                        emoji="🤖"
                    )
                
                # Log inputs
                if settings.trace_agent_inputs:
                    logger.debug(
                        f"📥 Agent Input",
                        agent=agent_name,
                        trace_id=trace_id,
                        input_keys=list(state.keys()),
                        emoji="📥"
                    )
                
                try:
                    # Execute agent
                    result = await func(state, *args, **kwargs)
                    duration_ms = (time.time() - start_time) * 1000
                    
                    # Log outputs
                    if settings.trace_agent_outputs:
                        logger.debug(
                            f"📤 Agent Output",
                            agent=agent_name,
                            trace_id=trace_id,
                            output_keys=list(result.keys()),
                            emoji="📤"
                        )
                    
                    # Log completion
                    if settings.trace_agent_timing:
                        logger.info(
                            f"⏱️  Agent Completed: {agent_name}",
                            agent=agent_name,
                            trace_id=trace_id,
                            duration_ms=round(duration_ms, 2),
                            status="success",
                            emoji="⏱️"
                        )
                    
                    # Add to trace
                    if 'agent_trace' not in result:
                        result['agent_trace'] = []
                    
                    result['agent_trace'].append({
                        'agent': agent_name,
                        'duration_ms': round(duration_ms, 2),
                        'status': 'success',
                        'timestamp': time.time()
                    })
                    
                    # Slow query warning
                    if duration_ms > settings.slow_query_threshold_ms:
                        logger.warning(
                            f"🐌 Slow Agent Execution",
                            agent=agent_name,
                            duration_ms=round(duration_ms, 2),
                            threshold_ms=settings.slow_query_threshold_ms,
                            emoji="🐌"
                        )
                    
                    return result
                
                except Exception as e:
                    duration_ms = (time.time() - start_time) * 1000
                    
                    logger.error(
                        f"❌ Agent Failed: {agent_name}",
                        agent=agent_name,
                        trace_id=trace_id,
                        error=str(e),
                        error_type=type(e).__name__,
                        duration_ms=round(duration_ms, 2),
                        emoji="❌",
                        exc_info=True
                    )
                    
                    raise
            
            return wrapper
        return decorator

# Global tracer instance
tracer = AgentTracer()
```

#### 0.4 LLM Tracer
**File**: `backend/app/utils/llm_tracer.py`

```python
from app.utils.logger import logger
from app.config import settings

class LLMTracer:
    """Trace LLM API calls with cost estimation"""
    
    @staticmethod
    async def trace_llm_call(
        model_id: str,
        prompt: str,
        response: str,
        tokens_input: int,
        tokens_output: int,
        duration_ms: float,
        trace_id: str
    ):
        """Log LLM call with detailed metrics"""
        
        cost = LLMTracer._estimate_cost(model_id, tokens_input, tokens_output)
        
        if settings.trace_llm_calls:
            logger.info(
                "🧠 LLM Call - Claude Sonnet 4.6",
                model=model_id,
                trace_id=trace_id,
                tokens_input=tokens_input,
                tokens_output=tokens_output,
                total_tokens=tokens_input + tokens_output,
                duration_ms=round(duration_ms, 2),
                cost_usd=cost,
                emoji="🧠"
            )
        
        if settings.trace_llm_prompts:
            logger.debug(
                "📝 LLM Prompt",
                model=model_id,
                trace_id=trace_id,
                prompt=prompt[:500] + "..." if len(prompt) > 500 else prompt,
                prompt_length=len(prompt),
                emoji="📝"
            )
        
        if settings.trace_llm_responses:
            logger.debug(
                "💬 LLM Response",
                model=model_id,
                trace_id=trace_id,
                response=response[:500] + "..." if len(response) > 500 else response,
                response_length=len(response),
                emoji="💬"
            )
    
    @staticmethod
    def _estimate_cost(model_id: str, tokens_input: int, tokens_output: int) -> float:
        """Estimate cost for Claude Sonnet 4.6"""
        # Claude Sonnet 4.6 pricing (Feb 2026)
        if "claude-sonnet-4-6" in model_id:
            cost_per_1k_input = 0.003   # $3 per 1M input tokens
            cost_per_1k_output = 0.015  # $15 per 1M output tokens
        else:
            # Fallback pricing
            cost_per_1k_input = 0.003
            cost_per_1k_output = 0.015
        
        cost = (tokens_input / 1000 * cost_per_1k_input) + \
               (tokens_output / 1000 * cost_per_1k_output)
        
        return round(cost, 6)

llm_tracer = LLMTracer()
```

### **Testing Phase 0**

```python
# Test logging
from app.utils.logger import logger

logger.debug("Debug message", key="value")
logger.info("Info message", emoji="✅")
logger.warning("Warning message", emoji="⚠️")
logger.error("Error message", emoji="❌")

# Test agent tracer
from app.utils.tracing import tracer

@tracer.trace_agent("TestAgent")
async def test_agent(state):
    await asyncio.sleep(0.1)
    return state

# Test LLM tracer
from app.utils.llm_tracer import llm_tracer

await llm_tracer.trace_llm_call(
    model_id="anthropic.claude-sonnet-4-6-20260223-v1:0",
    prompt="Test prompt",
    response="Test response",
    tokens_input=100,
    tokens_output=50,
    duration_ms=1500,
    trace_id="test_123"
)
```

**Expected Output**:
```
2026-03-05 14:00:00 [INFO] 🤖 Agent Started: TestAgent
2026-03-05 14:00:00 [INFO] ⏱️  Agent Completed: TestAgent duration_ms=100.5
2026-03-05 14:00:00 [INFO] 🧠 LLM Call - Claude Sonnet 4.6 tokens=150 cost_usd=0.001050
```

---

## ✅ Phase 0 Checklist

- [ ] Debug configuration created
- [ ] Structured logging working
- [ ] Agent tracer decorator functional
- [ ] LLM tracer implemented
- [ ] Emoji indicators displaying correctly
- [ ] Log files being created
- [ ] JSON format working
- [ ] Console colors enabled

---

## 🚀 Phase 1-5 Summary

**Phase 1**: Project structure, dependencies, environment setup  
**Phase 2**: FastAPI, services, agents with tracing decorators  
**Phase 3**: React frontend with agent trace visualization  
**Phase 4**: AWS deployment with CloudWatch integration  
**Phase 5**: End-to-end testing, demo preparation  

---

## 📊 Debug Output Examples

### **Development Mode (Console)**
```bash
2026-03-05 14:05:23 [INFO] 🤖 Agent Started: QueryAnalyzerAgent
2026-03-05 14:05:23 [DEBUG] 📥 Agent Input input_keys=['request_id', 'user_query']
2026-03-05 14:05:23 [DEBUG] Analyzing query query="What are the side effects?"
2026-03-05 14:05:23 [DEBUG] Intent classified as factual lookup
2026-03-05 14:05:23 [DEBUG] 📤 Agent Output output_keys=['intent', 'strategy']
2026-03-05 14:05:23 [INFO] ⏱️  Agent Completed: QueryAnalyzerAgent duration_ms=45.2

2026-03-05 14:05:23 [INFO] 🤖 Agent Started: RetrievalAgent
2026-03-05 14:05:24 [INFO] ⏱️  Agent Completed: RetrievalAgent duration_ms=234.5

2026-03-05 14:05:24 [INFO] 🤖 Agent Started: RerankingAgent
2026-03-05 14:05:24 [INFO] ⏱️  Agent Completed: RerankingAgent duration_ms=156.8

2026-03-05 14:05:24 [INFO] 🤖 Agent Started: SynthesisAgent
2026-03-05 14:05:24 [DEBUG] 📝 LLM Prompt prompt="You are a medical..."
2026-03-05 14:05:26 [INFO] 🧠 LLM Call - Claude Sonnet 4.6 tokens=1690 cost_usd=0.010554
2026-03-05 14:05:26 [DEBUG] 💬 LLM Response response="The common side effects..."
2026-03-05 14:05:26 [INFO] ⏱️  Agent Completed: SynthesisAgent duration_ms=1567.8

✅ Query processed successfully in 2.3s
```

### **Production Mode (JSON)**
```json
{"event":"Agent Started","agent":"QueryAnalyzerAgent","trace_id":"req_abc123","timestamp":"2026-03-05T14:05:23.123Z","level":"info"}
{"event":"Agent Completed","agent":"QueryAnalyzerAgent","duration_ms":45.2,"status":"success","timestamp":"2026-03-05T14:05:23.168Z","level":"info"}
{"event":"LLM Call","model":"anthropic.claude-sonnet-4-6-20260223-v1:0","tokens_input":1234,"tokens_output":456,"cost_usd":0.010554,"timestamp":"2026-03-05T14:05:26.123Z","level":"info"}
```

---

## 🎯 Key Benefits of Debug System

1. **Real-time Visibility**: See exactly what each agent is doing
2. **Performance Monitoring**: Identify slow agents immediately
3. **Cost Tracking**: Monitor LLM token usage and costs
4. **Error Debugging**: Quickly locate failures in the workflow
5. **Interview Demo**: Showcase sophisticated observability
6. **Production Ready**: Structured logs for CloudWatch

---

**Implementation Guide Version**: 2.0  
**Updated**: March 5, 2026  
**Status**: Ready for Development
