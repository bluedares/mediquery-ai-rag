"""
Agent Execution Tracer with Comprehensive Logging
"""

import time
import functools
import uuid
from typing import Any, Callable, Dict, List
from app.config import settings
from app.utils.logger import logger


class AgentTracer:
    """
    Comprehensive agent execution tracer with detailed logging
    
    Features:
    - Automatic timing
    - Input/output logging
    - Error capture
    - State tracking
    - Slow query detection
    - Trace aggregation
    """
    
    def __init__(self):
        self.traces: Dict[str, List[Dict]] = {}
    
    def trace_agent(self, agent_name: str):
        """
        Decorator to trace agent execution with detailed logging
        
        Usage:
            @tracer.trace_agent("MyAgent")
            async def my_agent(state: dict) -> dict:
                # Agent logic
                return state
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            async def wrapper(state: dict, *args, **kwargs) -> dict:
                # Get trace ID from state
                trace_id = state.get('request_id', str(uuid.uuid4()))
                
                # Start timing
                start_time = time.time()
                
                # Log agent start
                if settings.trace_agents:
                    logger.info(
                        f"🤖 Agent Started: {agent_name}",
                        agent=agent_name,
                        trace_id=trace_id,
                        state_keys=list(state.keys()) if settings.trace_agent_state else None
                    )
                
                # Log inputs
                if settings.trace_agent_inputs:
                    sanitized_input = self._sanitize_state(state)
                    logger.debug(
                        f"📥 Agent Input: {agent_name}",
                        agent=agent_name,
                        trace_id=trace_id,
                        input_state=sanitized_input
                    )
                
                try:
                    # Execute agent
                    result = await func(state, *args, **kwargs)
                    
                    # Calculate duration
                    duration_ms = (time.time() - start_time) * 1000
                    
                    # Log outputs
                    if settings.trace_agent_outputs:
                        sanitized_output = self._sanitize_state(result)
                        logger.debug(
                            f"📤 Agent Output: {agent_name}",
                            agent=agent_name,
                            trace_id=trace_id,
                            output_state=sanitized_output
                        )
                    
                    # Log completion
                    if settings.trace_agent_timing:
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
                    
                    trace_entry = {
                        'agent': agent_name,
                        'duration_ms': round(duration_ms, 2),
                        'status': 'success',
                        'timestamp': time.time(),
                        'start_time': start_time,
                        'end_time': time.time()
                    }
                    
                    result['agent_trace'].append(trace_entry)
                    
                    # Store trace
                    if trace_id not in self.traces:
                        self.traces[trace_id] = []
                    self.traces[trace_id].append(trace_entry)
                    
                    # Check for slow execution
                    if duration_ms > settings.slow_agent_threshold_ms:
                        logger.warning(
                            f"🐌 Slow Agent Execution: {agent_name}",
                            agent=agent_name,
                            trace_id=trace_id,
                            duration_ms=round(duration_ms, 2),
                            threshold_ms=settings.slow_agent_threshold_ms
                        )
                    
                    return result
                
                except Exception as e:
                    # Calculate duration
                    duration_ms = (time.time() - start_time) * 1000
                    
                    # Log error
                    logger.error(
                        f"❌ Agent Failed: {agent_name}",
                        agent=agent_name,
                        trace_id=trace_id,
                        error=str(e),
                        error_type=type(e).__name__,
                        duration_ms=round(duration_ms, 2),
                        exc_info=settings.include_stack_trace
                    )
                    
                    # Add error to state
                    if 'errors' not in state:
                        state['errors'] = []
                    
                    state['errors'].append({
                        'agent': agent_name,
                        'error': str(e),
                        'error_type': type(e).__name__,
                        'timestamp': time.time()
                    })
                    
                    # Add failed trace
                    if 'agent_trace' not in state:
                        state['agent_trace'] = []
                    
                    state['agent_trace'].append({
                        'agent': agent_name,
                        'duration_ms': round(duration_ms, 2),
                        'status': 'failed',
                        'error': str(e),
                        'timestamp': time.time()
                    })
                    
                    # Re-raise exception
                    raise
            
            return wrapper
        return decorator
    
    def _sanitize_state(self, state: dict) -> dict:
        """
        Remove sensitive or verbose data from state for logging
        
        Args:
            state: Agent state dictionary
            
        Returns:
            Sanitized state dictionary
        """
        sanitized = {}
        
        for key, value in state.items():
            # Handle large lists (like chunks)
            if key in ['retrieved_chunks', 'reranked_chunks']:
                if isinstance(value, list):
                    sanitized[key] = f"<{len(value)} items>"
                else:
                    sanitized[key] = "<unknown>"
            
            # Truncate long strings
            elif key in ['final_answer', 'user_query']:
                if isinstance(value, str):
                    max_len = 200
                    sanitized[key] = value[:max_len] + "..." if len(value) > max_len else value
                else:
                    sanitized[key] = value
            
            # Keep simple types
            elif isinstance(value, (str, int, float, bool, type(None))):
                sanitized[key] = value
            
            # Represent complex types
            elif isinstance(value, list):
                sanitized[key] = f"<list of {len(value)} items>"
            elif isinstance(value, dict):
                sanitized[key] = f"<dict with {len(value)} keys>"
            else:
                sanitized[key] = f"<{type(value).__name__}>"
        
        return sanitized
    
    def get_trace(self, trace_id: str) -> List[Dict]:
        """
        Get trace for a specific request
        
        Args:
            trace_id: Request trace ID
            
        Returns:
            List of trace entries
        """
        return self.traces.get(trace_id, [])
    
    def clear_trace(self, trace_id: str):
        """
        Clear trace for a specific request
        
        Args:
            trace_id: Request trace ID
        """
        if trace_id in self.traces:
            del self.traces[trace_id]
    
    def get_all_traces(self) -> Dict[str, List[Dict]]:
        """
        Get all traces
        
        Returns:
            Dictionary of all traces
        """
        return self.traces
    
    def clear_all_traces(self):
        """Clear all traces"""
        self.traces.clear()


# Global tracer instance
tracer = AgentTracer()
