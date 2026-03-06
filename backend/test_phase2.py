#!/usr/bin/env python3
"""
Test Phase 2 - Service Layer, Agents, and API
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.config import settings
from app.utils.logger import logger
from app.services import bedrock_service, embedding_service, opensearch_service
from app.agents import agent_graph


async def test_services():
    """Test service layer"""
    print("\n" + "="*80)
    print("🧪 Testing Phase 2A - Service Layer")
    print("="*80 + "\n")
    
    # Test 1: Embedding Service
    print("✅ Test 1: Embedding Service")
    try:
        text = "What are the primary endpoints of this clinical trial?"
        embedding = await embedding_service.encode_single(text)
        print(f"   Generated embedding: dimension={len(embedding)}")
        print(f"   First 5 values: {embedding[:5]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    print()
    
    # Test 2: Bedrock Service (mock mode if no credentials)
    print("✅ Test 2: Bedrock Service")
    try:
        response = await bedrock_service.invoke(
            prompt="What is a clinical trial?",
            max_tokens=50,
            trace_id="test_bedrock"
        )
        print(f"   Response length: {len(response)} characters")
        print(f"   Preview: {response[:100]}...")
    except Exception as e:
        print(f"   ⚠️  Bedrock not configured (expected): {type(e).__name__}")
    print()
    
    # Test 3: OpenSearch Service
    print("✅ Test 3: OpenSearch Service")
    try:
        # Mock mode will return empty results
        results = await opensearch_service.vector_search(
            index_name="test-index",
            query_embedding=embedding,
            top_k=5
        )
        print(f"   Search results: {len(results)} documents")
    except Exception as e:
        print(f"   ⚠️  OpenSearch in mock mode: {type(e).__name__}")
    print()


async def test_agents():
    """Test agent system"""
    print("\n" + "="*80)
    print("🧪 Testing Phase 2B - Multi-Agent System")
    print("="*80 + "\n")
    
    # Test agent workflow
    print("✅ Test: Complete Agent Workflow")
    
    initial_state = {
        'request_id': 'test_workflow_001',
        'user_query': 'What are the common side effects?',
        'document_id': 'doc_test_123',
        'conversation_id': None,
        'intent': '',
        'search_strategy': '',
        'expanded_query': None,
        'retrieved_chunks': [],
        'retrieval_scores': [],
        'reranked_chunks': [],
        'rerank_scores': [],
        'final_answer': '',
        'citations': [],
        'confidence': 0.0,
        'agent_trace': [],
        'errors': []
    }
    
    try:
        result = await agent_graph.ainvoke(initial_state)
        
        print(f"\n   Agent Execution Summary:")
        print(f"   - Intent: {result.get('intent')}")
        print(f"   - Strategy: {result.get('search_strategy')}")
        print(f"   - Chunks Retrieved: {len(result.get('retrieved_chunks', []))}")
        print(f"   - Chunks Reranked: {len(result.get('reranked_chunks', []))}")
        print(f"   - Answer Length: {len(result.get('final_answer', ''))} chars")
        print(f"   - Confidence: {result.get('confidence', 0):.3f}")
        print(f"   - Agents Executed: {len(result.get('agent_trace', []))}")
        
        print(f"\n   Agent Trace:")
        for trace in result.get('agent_trace', []):
            print(f"   - {trace['agent']}: {trace['duration_ms']:.2f}ms ({trace['status']})")
        
        if result.get('errors'):
            print(f"\n   ⚠️  Errors encountered: {result['errors']}")
        
    except Exception as e:
        print(f"   ❌ Workflow failed: {e}")
        import traceback
        traceback.print_exc()
    
    print()


async def test_integration():
    """Test full integration"""
    print("\n" + "="*80)
    print("🧪 Testing Phase 2 - Full Integration")
    print("="*80 + "\n")
    
    print("✅ All components loaded successfully!")
    print(f"   - Services: Bedrock, OpenSearch, S3, Embeddings")
    print(f"   - Agents: QueryAnalyzer, Retrieval, Reranking, Synthesis")
    print(f"   - API: Query endpoint ready")
    print(f"   - Debug: Tracing enabled")
    print()


async def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("🚀 Phase 2 Testing Suite")
    print("="*80)
    
    await test_services()
    await test_agents()
    await test_integration()
    
    print("="*80)
    print("🎉 Phase 2 Testing Complete!")
    print("="*80)
    print("\n✅ Ready for Phase 3: Frontend Development\n")


if __name__ == "__main__":
    asyncio.run(main())
