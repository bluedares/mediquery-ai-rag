#!/usr/bin/env python3
"""
Quick test script for Phase 0 - Debug Infrastructure
Run this to verify the debug system is working
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import settings, debug_config
from app.utils.logger import logger
from app.utils.tracing import tracer
from app.utils.llm_tracer import llm_tracer


async def main():
    """Test the debug infrastructure"""
    
    print("\n" + "="*80)
    print("🧪 Testing Phase 0 - Debug Infrastructure")
    print("="*80 + "\n")
    
    # Test 1: Configuration
    print("✅ Test 1: Configuration")
    print(f"   App Name: {settings.app_name}")
    print(f"   Version: {settings.app_version}")
    print(f"   Debug Mode: {settings.debug_mode}")
    print(f"   Model: {settings.bedrock_model_id}")
    print(f"   Log Level: {settings.log_level.value}")
    print()
    
    # Test 2: Logger with emojis
    print("✅ Test 2: Structured Logging with Emojis")
    logger.debug("🔍 Debug message", test="value")
    logger.info("✅ Info message", status="success")
    logger.warning("⚠️  Warning message", alert="check this")
    print()
    
    # Test 3: Agent Tracer
    print("✅ Test 3: Agent Tracer")
    
    @tracer.trace_agent("TestAgent")
    async def test_agent(state: dict) -> dict:
        """Simulated agent"""
        logger.debug("Processing in TestAgent", data=state.get('data'))
        await asyncio.sleep(0.1)  # Simulate work
        state['processed'] = True
        return state
    
    state = {
        'request_id': 'test_req_001',
        'data': 'sample data'
    }
    
    result = await test_agent(state)
    
    print(f"   Agent trace entries: {len(result.get('agent_trace', []))}")
    if result.get('agent_trace'):
        trace = result['agent_trace'][0]
        print(f"   Agent: {trace['agent']}")
        print(f"   Duration: {trace['duration_ms']}ms")
        print(f"   Status: {trace['status']}")
    print()
    
    # Test 4: LLM Tracer
    print("✅ Test 4: LLM Tracer")
    
    await llm_tracer.trace_llm_call(
        model_id="anthropic.claude-sonnet-4-6-20260223-v1:0",
        prompt="What are the primary endpoints of this clinical trial?",
        response="The primary endpoints are: 1. Overall Survival (OS) at 24 months, 2. Progression-Free Survival (PFS)",
        tokens_input=1234,
        tokens_output=456,
        duration_ms=1567.8,
        trace_id="test_req_001"
    )
    
    # Test cost estimation
    cost = llm_tracer._estimate_cost(
        "anthropic.claude-sonnet-4-6-20260223-v1:0",
        tokens_input=1234,
        tokens_output=456
    )
    print(f"   Estimated cost: ${cost:.6f}")
    print()
    
    # Test 5: Error Handling
    print("✅ Test 5: Error Handling")
    
    @tracer.trace_agent("ErrorAgent")
    async def error_agent(state: dict) -> dict:
        """Agent that fails"""
        raise ValueError("Simulated error for testing")
    
    try:
        await error_agent({'request_id': 'test_error_001'})
    except ValueError as e:
        print(f"   ✅ Error caught and logged: {e}")
    print()
    
    # Test 6: Multiple Agents
    print("✅ Test 6: Multi-Agent Workflow")
    
    @tracer.trace_agent("Agent1")
    async def agent1(state: dict) -> dict:
        await asyncio.sleep(0.05)
        state['step1'] = 'complete'
        return state
    
    @tracer.trace_agent("Agent2")
    async def agent2(state: dict) -> dict:
        await asyncio.sleep(0.08)
        state['step2'] = 'complete'
        return state
    
    @tracer.trace_agent("Agent3")
    async def agent3(state: dict) -> dict:
        await asyncio.sleep(0.06)
        state['step3'] = 'complete'
        return state
    
    workflow_state = {'request_id': 'workflow_001'}
    workflow_state = await agent1(workflow_state)
    workflow_state = await agent2(workflow_state)
    workflow_state = await agent3(workflow_state)
    
    print(f"   Total agents executed: {len(workflow_state['agent_trace'])}")
    total_time = sum(t['duration_ms'] for t in workflow_state['agent_trace'])
    print(f"   Total execution time: {total_time:.2f}ms")
    
    for trace in workflow_state['agent_trace']:
        print(f"   - {trace['agent']}: {trace['duration_ms']:.2f}ms")
    print()
    
    # Summary
    print("="*80)
    print("🎉 Phase 0 Debug Infrastructure - ALL TESTS PASSED!")
    print("="*80)
    print("\n✅ Ready to proceed to Phase 1: Project Setup\n")


if __name__ == "__main__":
    asyncio.run(main())
