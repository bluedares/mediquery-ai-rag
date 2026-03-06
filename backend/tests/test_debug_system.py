"""
Test Debug System - Phase 0
"""

import pytest
import asyncio
from app.config import settings, debug_config
from app.utils.logger import logger
from app.utils.tracing import tracer
from app.utils.llm_tracer import llm_tracer


def test_settings_loaded():
    """Test that settings are loaded correctly"""
    assert settings.app_name == "MediQuery AI"
    assert settings.bedrock_model_id == "anthropic.claude-sonnet-4-6-20260223-v1:0"
    assert settings.debug_mode is True


def test_debug_config():
    """Test debug configuration helper"""
    assert debug_config.is_debug_mode() is True
    assert debug_config.should_trace_agents() is True
    assert debug_config.should_trace_llm() is True
    assert debug_config.is_production() is False


def test_logger_initialization():
    """Test logger is initialized"""
    assert logger is not None
    
    # Test logging
    logger.debug("Test debug message", test_key="test_value")
    logger.info("Test info message", emoji="✅")
    logger.warning("Test warning message", emoji="⚠️")


@pytest.mark.asyncio
async def test_agent_tracer():
    """Test agent tracer decorator"""
    
    @tracer.trace_agent("TestAgent")
    async def test_agent(state: dict) -> dict:
        """Test agent function"""
        await asyncio.sleep(0.1)
        state['processed'] = True
        return state
    
    # Execute agent
    initial_state = {
        'request_id': 'test_123',
        'test_data': 'hello'
    }
    
    result = await test_agent(initial_state)
    
    # Verify trace was added
    assert 'agent_trace' in result
    assert len(result['agent_trace']) == 1
    assert result['agent_trace'][0]['agent'] == 'TestAgent'
    assert result['agent_trace'][0]['status'] == 'success'
    assert result['agent_trace'][0]['duration_ms'] > 0
    
    # Verify state was modified
    assert result['processed'] is True


@pytest.mark.asyncio
async def test_agent_tracer_error_handling():
    """Test agent tracer error handling"""
    
    @tracer.trace_agent("ErrorAgent")
    async def error_agent(state: dict) -> dict:
        """Agent that raises an error"""
        raise ValueError("Test error")
    
    initial_state = {
        'request_id': 'test_error_123'
    }
    
    # Should raise the error
    with pytest.raises(ValueError):
        await error_agent(initial_state)
    
    # Verify error was logged in state
    assert 'errors' in initial_state
    assert len(initial_state['errors']) == 1
    assert initial_state['errors'][0]['agent'] == 'ErrorAgent'
    assert 'Test error' in initial_state['errors'][0]['error']


@pytest.mark.asyncio
async def test_llm_tracer():
    """Test LLM tracer"""
    
    await llm_tracer.trace_llm_call(
        model_id="anthropic.claude-sonnet-4-6-20260223-v1:0",
        prompt="Test prompt for medical question",
        response="Test response with medical information",
        tokens_input=100,
        tokens_output=50,
        duration_ms=1500.5,
        trace_id="test_llm_123"
    )
    
    # If we get here without errors, the tracer works
    assert True


def test_llm_cost_estimation():
    """Test LLM cost estimation"""
    
    # Test Claude Sonnet 4.6 pricing
    cost = llm_tracer._estimate_cost(
        "anthropic.claude-sonnet-4-6-20260223-v1:0",
        tokens_input=1000,
        tokens_output=500
    )
    
    # Expected: (1000/1000 * 0.003) + (500/1000 * 0.015) = 0.003 + 0.0075 = 0.0105
    assert cost == 0.0105
    
    # Test with larger numbers
    cost_large = llm_tracer._estimate_cost(
        "anthropic.claude-sonnet-4-6-20260223-v1:0",
        tokens_input=10000,
        tokens_output=5000
    )
    
    # Expected: (10000/1000 * 0.003) + (5000/1000 * 0.015) = 0.03 + 0.075 = 0.105
    assert cost_large == 0.105


def test_token_estimation():
    """Test token estimation"""
    
    text = "This is a test sentence for token estimation."
    tokens = llm_tracer.estimate_tokens(text)
    
    # Should be roughly len(text) / 4
    expected = len(text) // 4
    assert tokens == expected


def test_tracer_state_sanitization():
    """Test state sanitization"""
    
    state = {
        'user_query': 'What are the side effects?' * 50,  # Long string
        'retrieved_chunks': [{'text': 'chunk1'}, {'text': 'chunk2'}],
        'simple_value': 42,
        'boolean_value': True,
        'none_value': None
    }
    
    sanitized = tracer._sanitize_state(state)
    
    # Long string should be truncated
    assert len(sanitized['user_query']) <= 203  # 200 + "..."
    
    # Chunks should be summarized
    assert '<2 items>' in sanitized['retrieved_chunks']
    
    # Simple values should be preserved
    assert sanitized['simple_value'] == 42
    assert sanitized['boolean_value'] is True
    assert sanitized['none_value'] is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
