# Debug & Tracing System - MediQuery AI

## 🔍 Global Debug Architecture

This document describes the comprehensive debug and tracing system for monitoring multi-agent workflows.

---

## 🎯 Objectives

1. **Agent Visibility**: Track what each agent is doing in real-time
2. **Performance Monitoring**: Measure latency at each step
3. **Error Debugging**: Quickly identify where failures occur
4. **Production Observability**: Maintain debug capabilities in production
5. **Interview Demo**: Showcase agent collaboration visually

---

## 🏗️ Debug System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Application Layer                       │
│  ┌──────────────────────────────────────────────────┐   │
│  │         LangGraph Agent Execution                │   │
│  │  ┌────────────────────────────────────────────┐  │   │
│  │  │  Agent 1 → Agent 2 → Agent 3 → Agent 4    │  │   │
│  │  │     ↓         ↓         ↓         ↓        │  │   │
│  │  │  [Trace]  [Trace]  [Trace]  [Trace]       │  │   │
│  │  └────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                  │
┌───────▼────────┐              ┌─────────▼──────────┐
│  Structured    │              │  Distributed       │
│  Logging       │              │  Tracing           │
│  (Loguru +     │              │  (OpenTelemetry +  │
│   Structlog)   │              │   AWS X-Ray)       │
└───────┬────────┘              └─────────┬──────────┘
        │                                  │
        └────────────────┬─────────────────┘
                         │
        ┌────────────────▼────────────────┐
        │                                  │
┌───────▼────────┐              ┌─────────▼──────────┐
│  CloudWatch    │              │  Local Console     │
│  Logs          │              │  (Development)     │
└────────────────┘              └────────────────────┘
```

---

## 🔧 Implementation Components

### **1. Global Debug Configuration**

**File**: `backend/app/config.py`

```python
from pydantic_settings import BaseSettings
from enum import Enum

class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"

class DebugConfig(BaseSettings):
    """Debug and tracing configuration"""
    
    # Global debug flag
    DEBUG_MODE: bool = True  # Set to False in production
    
    # Logging
    LOG_LEVEL: LogLevel = LogLevel.DEBUG
    LOG_FORMAT: str = "json"  # json or console
    LOG_TO_FILE: bool = True
    LOG_FILE_PATH: str = "logs/mediquery.log"
    
    # Agent tracing
    TRACE_AGENTS: bool = True
    TRACE_AGENT_INPUTS: bool = True
    TRACE_AGENT_OUTPUTS: bool = True
    TRACE_AGENT_TIMING: bool = True
    TRACE_AGENT_STATE: bool = True
    
    # LLM tracing
    TRACE_LLM_CALLS: bool = True
    TRACE_LLM_PROMPTS: bool = True
    TRACE_LLM_RESPONSES: bool = True
    TRACE_LLM_TOKENS: bool = True
    
    # Performance monitoring
    ENABLE_PERFORMANCE_METRICS: bool = True
    SLOW_QUERY_THRESHOLD_MS: int = 3000
    
    # Distributed tracing
    ENABLE_XRAY: bool = True
    ENABLE_OPENTELEMETRY: bool = True
    
    # Debug output
    PRINT_AGENT_TRACE: bool = True  # Console output
    SAVE_TRACE_TO_DB: bool = True   # Persist traces
    
    class Config:
        env_file = ".env"

debug_config = DebugConfig()
```

---

### **2. Structured Logging Setup**

**File**: `backend/app/utils/logger.py`

```python
import structlog
import logging
import sys
from pathlib import Path
from app.config import debug_config

def setup_logging():
    """Configure structured logging"""
    
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
            structlog.processors.JSONRenderer() if debug_config.LOG_FORMAT == "json"
            else structlog.dev.ConsoleRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(debug_config.LOG_LEVEL)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # File handler
    if debug_config.LOG_TO_FILE:
        file_handler = logging.FileHandler(debug_config.LOG_FILE_PATH)
        file_handler.setLevel(logging.DEBUG)
        logging.root.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if debug_config.DEBUG_MODE else logging.INFO)
    logging.root.addHandler(console_handler)
    
    return structlog.get_logger()

logger = setup_logging()
```

---

### **3. Agent Tracer Decorator**

**File**: `backend/app/utils/tracing.py`

```python
import time
import functools
import uuid
from typing import Any, Callable
from app.utils.logger import logger
from app.config import debug_config
import json

class AgentTracer:
    """Trace agent execution with detailed logging"""
    
    def __init__(self):
        self.traces = {}
    
    def trace_agent(self, agent_name: str):
        """Decorator to trace agent execution"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            async def wrapper(state: dict, *args, **kwargs) -> dict:
                trace_id = state.get('request_id', str(uuid.uuid4()))
                
                # Start trace
                start_time = time.time()
                
                if debug_config.TRACE_AGENTS:
                    logger.info(
                        f"🤖 Agent Started: {agent_name}",
                        agent=agent_name,
                        trace_id=trace_id,
                        state_keys=list(state.keys())
                    )
                
                # Log inputs
                if debug_config.TRACE_AGENT_INPUTS:
                    logger.debug(
                        f"📥 Agent Input: {agent_name}",
                        agent=agent_name,
                        trace_id=trace_id,
                        input_state=self._sanitize_state(state)
                    )
                
                try:
                    # Execute agent
                    result = await func(state, *args, **kwargs)
                    
                    # Calculate duration
                    duration_ms = (time.time() - start_time) * 1000
                    
                    # Log outputs
                    if debug_config.TRACE_AGENT_OUTPUTS:
                        logger.debug(
                            f"📤 Agent Output: {agent_name}",
                            agent=agent_name,
                            trace_id=trace_id,
                            output_state=self._sanitize_state(result),
                            duration_ms=round(duration_ms, 2)
                        )
                    
                    # Log timing
                    if debug_config.TRACE_AGENT_TIMING:
                        logger.info(
                            f"⏱️  Agent Completed: {agent_name}",
                            agent=agent_name,
                            trace_id=trace_id,
                            duration_ms=round(duration_ms, 2),
                            status="success"
                        )
                    
                    # Add trace to state
                    if 'agent_trace' not in result:
                        result['agent_trace'] = []
                    
                    result['agent_trace'].append({
                        'agent': agent_name,
                        'duration_ms': round(duration_ms, 2),
                        'status': 'success',
                        'timestamp': time.time()
                    })
                    
                    # Check for slow execution
                    if duration_ms > debug_config.SLOW_QUERY_THRESHOLD_MS:
                        logger.warning(
                            f"🐌 Slow Agent Execution: {agent_name}",
                            agent=agent_name,
                            trace_id=trace_id,
                            duration_ms=round(duration_ms, 2),
                            threshold_ms=debug_config.SLOW_QUERY_THRESHOLD_MS
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
                        exc_info=True
                    )
                    
                    # Add error to state
                    if 'errors' not in state:
                        state['errors'] = []
                    state['errors'].append({
                        'agent': agent_name,
                        'error': str(e),
                        'error_type': type(e).__name__
                    })
                    
                    raise
            
            return wrapper
        return decorator
    
    def _sanitize_state(self, state: dict) -> dict:
        """Remove sensitive data from state for logging"""
        sanitized = {}
        for key, value in state.items():
            if key in ['retrieved_chunks', 'reranked_chunks']:
                # Only log count, not full content
                sanitized[key] = f"<{len(value)} chunks>"
            elif key == 'final_answer':
                # Truncate long answers
                sanitized[key] = value[:200] + "..." if len(value) > 200 else value
            elif isinstance(value, (str, int, float, bool)):
                sanitized[key] = value
            else:
                sanitized[key] = f"<{type(value).__name__}>"
        return sanitized

# Global tracer instance
tracer = AgentTracer()
```

---

### **4. LLM Call Tracer**

**File**: `backend/app/utils/llm_tracer.py`

```python
import time
from typing import Optional
from app.utils.logger import logger
from app.config import debug_config

class LLMTracer:
    """Trace LLM API calls"""
    
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
        """Log LLM call details"""
        
        if debug_config.TRACE_LLM_CALLS:
            logger.info(
                "🧠 LLM Call",
                model=model_id,
                trace_id=trace_id,
                tokens_input=tokens_input,
                tokens_output=tokens_output,
                duration_ms=round(duration_ms, 2),
                cost_estimate_usd=LLMTracer._estimate_cost(
                    model_id, tokens_input, tokens_output
                )
            )
        
        if debug_config.TRACE_LLM_PROMPTS:
            logger.debug(
                "📝 LLM Prompt",
                model=model_id,
                trace_id=trace_id,
                prompt=prompt[:500] + "..." if len(prompt) > 500 else prompt,
                prompt_length=len(prompt)
            )
        
        if debug_config.TRACE_LLM_RESPONSES:
            logger.debug(
                "💬 LLM Response",
                model=model_id,
                trace_id=trace_id,
                response=response[:500] + "..." if len(response) > 500 else response,
                response_length=len(response)
            )
    
    @staticmethod
    def _estimate_cost(model_id: str, tokens_input: int, tokens_output: int) -> float:
        """Estimate cost based on token usage"""
        # Claude Sonnet 4.6 pricing (example)
        if "claude-sonnet-4-6" in model_id:
            cost_per_1k_input = 0.003
            cost_per_1k_output = 0.015
        else:
            cost_per_1k_input = 0.003
            cost_per_1k_output = 0.015
        
        cost = (tokens_input / 1000 * cost_per_1k_input) + \
               (tokens_output / 1000 * cost_per_1k_output)
        
        return round(cost, 6)

llm_tracer = LLMTracer()
```

---

### **5. AWS X-Ray Integration**

**File**: `backend/app/utils/xray.py`

```python
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware
from app.config import debug_config

def setup_xray(app):
    """Setup AWS X-Ray tracing"""
    if debug_config.ENABLE_XRAY:
        xray_recorder.configure(
            service='MediQuery-API',
            sampling=True,
            context_missing='LOG_ERROR'
        )
        XRayMiddleware(app, xray_recorder)

def trace_segment(name: str):
    """Decorator for X-Ray segments"""
    def decorator(func):
        if debug_config.ENABLE_XRAY:
            return xray_recorder.capture(name)(func)
        return func
    return decorator

def trace_subsegment(name: str):
    """Decorator for X-Ray subsegments"""
    def decorator(func):
        if debug_config.ENABLE_XRAY:
            async def wrapper(*args, **kwargs):
                subsegment = xray_recorder.begin_subsegment(name)
                try:
                    result = await func(*args, **kwargs)
                    return result
                finally:
                    xray_recorder.end_subsegment()
            return wrapper
        return func
    return decorator
```

---

### **6. Agent Implementation with Tracing**

**File**: `backend/app/agents/query_analyzer.py` (Updated)

```python
from app.agents.graph import AgentState
from app.utils.tracing import tracer
from app.utils.logger import logger
import time

@tracer.trace_agent("QueryAnalyzerAgent")
async def query_analyzer_agent(state: AgentState) -> AgentState:
    """
    Analyze query and determine retrieval strategy
    
    This agent:
    1. Classifies user intent (factual, comparison, analysis)
    2. Determines optimal search strategy (semantic, keyword, hybrid)
    3. Expands query terms if needed
    """
    
    logger.debug(
        "Analyzing query",
        query=state['user_query'],
        query_length=len(state['user_query'])
    )
    
    # Intent classification logic
    query_lower = state['user_query'].lower()
    
    if any(word in query_lower for word in ['what', 'define', 'explain']):
        intent = 'factual_lookup'
        strategy = 'hybrid'
        logger.debug("Intent classified as factual lookup")
    elif any(word in query_lower for word in ['compare', 'difference', 'versus']):
        intent = 'comparison'
        strategy = 'semantic'
        logger.debug("Intent classified as comparison")
    elif any(word in query_lower for word in ['list', 'enumerate', 'all']):
        intent = 'enumeration'
        strategy = 'keyword'
        logger.debug("Intent classified as enumeration")
    else:
        intent = 'general_query'
        strategy = 'hybrid'
        logger.debug("Intent classified as general query")
    
    state['intent'] = intent
    state['search_strategy'] = strategy
    
    logger.info(
        "Query analysis complete",
        intent=intent,
        strategy=strategy
    )
    
    return state
```

---

### **7. Debug Endpoint**

**File**: `backend/app/api/debug.py`

```python
from fastapi import APIRouter, Query
from typing import Optional
from app.utils.logger import logger
from app.config import debug_config
import json

router = APIRouter()

@router.get("/debug/config")
async def get_debug_config():
    """Get current debug configuration"""
    return {
        "debug_mode": debug_config.DEBUG_MODE,
        "log_level": debug_config.LOG_LEVEL,
        "trace_agents": debug_config.TRACE_AGENTS,
        "trace_llm_calls": debug_config.TRACE_LLM_CALLS,
        "enable_xray": debug_config.ENABLE_XRAY
    }

@router.post("/debug/config")
async def update_debug_config(
    debug_mode: Optional[bool] = None,
    log_level: Optional[str] = None,
    trace_agents: Optional[bool] = None
):
    """Update debug configuration at runtime"""
    if debug_mode is not None:
        debug_config.DEBUG_MODE = debug_mode
    if log_level is not None:
        debug_config.LOG_LEVEL = log_level
    if trace_agents is not None:
        debug_config.TRACE_AGENTS = trace_agents
    
    logger.info("Debug configuration updated", config=debug_config.dict())
    return {"status": "updated", "config": debug_config.dict()}

@router.get("/debug/trace/{request_id}")
async def get_trace(request_id: str):
    """Get trace for a specific request"""
    # TODO: Retrieve from database
    return {"request_id": request_id, "trace": []}

@router.get("/debug/logs")
async def get_recent_logs(limit: int = Query(100, le=1000)):
    """Get recent log entries"""
    # TODO: Read from log file
    return {"logs": []}
```

---

### **8. Frontend Debug Visualization**

**File**: `frontend/src/components/AgentTraceViewer.tsx`

```typescript
import { useState } from 'react';

interface AgentTrace {
  agent: string;
  duration_ms: number;
  status: string;
  timestamp: number;
}

export function AgentTraceViewer({ trace }: { trace: AgentTrace[] }) {
  const [expanded, setExpanded] = useState(true);
  
  const totalDuration = trace.reduce((sum, t) => sum + t.duration_ms, 0);
  
  return (
    <div className="bg-gray-50 p-4 rounded-lg border">
      <div 
        className="flex items-center justify-between cursor-pointer"
        onClick={() => setExpanded(!expanded)}
      >
        <h3 className="font-bold text-lg">🔍 Agent Workflow Trace</h3>
        <span className="text-sm text-gray-600">
          Total: {totalDuration.toFixed(0)}ms
        </span>
      </div>
      
      {expanded && (
        <div className="mt-4 space-y-2">
          {trace.map((step, index) => (
            <div 
              key={index}
              className="flex items-center gap-3 p-3 bg-white rounded border"
            >
              <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-sm font-bold">
                {index + 1}
              </div>
              
              <div className="flex-grow">
                <div className="font-medium">{step.agent}</div>
                <div className="text-xs text-gray-500">
                  {new Date(step.timestamp * 1000).toLocaleTimeString()}
                </div>
              </div>
              
              <div className="flex items-center gap-2">
                <span className={`px-2 py-1 rounded text-xs ${
                  step.status === 'success' 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                }`}>
                  {step.status}
                </span>
                
                <span className="text-sm font-mono text-gray-600">
                  {step.duration_ms.toFixed(0)}ms
                </span>
              </div>
              
              {/* Progress bar */}
              <div className="w-24 bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-500 h-2 rounded-full"
                  style={{ 
                    width: `${(step.duration_ms / totalDuration) * 100}%` 
                  }}
                />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

---

## 📊 Debug Output Examples

### **Console Output (Development)**

```
2026-03-05 13:56:23 [INFO] 🤖 Agent Started: QueryAnalyzerAgent
  trace_id: req_abc123
  state_keys: ['request_id', 'user_query', 'document_id']

2026-03-05 13:56:23 [DEBUG] Analyzing query
  query: "What are the primary endpoints?"
  query_length: 31

2026-03-05 13:56:23 [DEBUG] Intent classified as factual lookup

2026-03-05 13:56:23 [INFO] Query analysis complete
  intent: factual_lookup
  strategy: hybrid

2026-03-05 13:56:23 [INFO] ⏱️  Agent Completed: QueryAnalyzerAgent
  duration_ms: 45.2
  status: success

2026-03-05 13:56:23 [INFO] 🤖 Agent Started: RetrievalAgent
  trace_id: req_abc123

2026-03-05 13:56:24 [INFO] ⏱️  Agent Completed: RetrievalAgent
  duration_ms: 234.5
  status: success
  chunks_retrieved: 20

2026-03-05 13:56:24 [INFO] 🧠 LLM Call
  model: anthropic.claude-sonnet-4-6-20260223-v1:0
  tokens_input: 1234
  tokens_output: 456
  duration_ms: 1567.8
  cost_estimate_usd: 0.010554
```

### **JSON Logs (Production)**

```json
{
  "event": "Agent Started",
  "agent": "QueryAnalyzerAgent",
  "trace_id": "req_abc123",
  "timestamp": "2026-03-05T13:56:23.123Z",
  "level": "info"
}
{
  "event": "Agent Completed",
  "agent": "QueryAnalyzerAgent",
  "trace_id": "req_abc123",
  "duration_ms": 45.2,
  "status": "success",
  "timestamp": "2026-03-05T13:56:23.168Z",
  "level": "info"
}
```

---

## 🎯 Interview Demo Usage

### **Showcase Debug Capabilities**

1. **Enable Debug Mode**:
```bash
export DEBUG_MODE=true
export TRACE_AGENTS=true
export PRINT_AGENT_TRACE=true
```

2. **Run Query with Tracing**:
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the side effects?", "document_id": "doc_123"}'
```

3. **Show Console Output**:
- Real-time agent execution
- Timing for each step
- LLM token usage
- Cost estimates

4. **Show Frontend Visualization**:
- Agent workflow diagram
- Progress bars
- Timing breakdown

---

## 🔧 Configuration Presets

### **Development**
```python
DEBUG_MODE = True
LOG_LEVEL = "DEBUG"
TRACE_AGENTS = True
TRACE_LLM_CALLS = True
PRINT_AGENT_TRACE = True
```

### **Staging**
```python
DEBUG_MODE = True
LOG_LEVEL = "INFO"
TRACE_AGENTS = True
TRACE_LLM_CALLS = True
PRINT_AGENT_TRACE = False
```

### **Production**
```python
DEBUG_MODE = False
LOG_LEVEL = "WARNING"
TRACE_AGENTS = True  # Keep for debugging
TRACE_LLM_CALLS = False  # Reduce noise
PRINT_AGENT_TRACE = False
```

---

## 📈 Performance Impact

| Feature | Overhead | Recommendation |
|---------|----------|----------------|
| Agent Tracing | ~5ms per agent | Always enable |
| LLM Prompt Logging | ~2ms | Enable in dev/staging |
| State Logging | ~10ms | Enable selectively |
| X-Ray Tracing | ~15ms | Enable in production |
| Console Output | ~20ms | Disable in production |

---

**Debug System Version**: 1.0  
**Last Updated**: March 5, 2026  
**Status**: Ready for Implementation
