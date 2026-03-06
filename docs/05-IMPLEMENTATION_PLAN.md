# Implementation Plan - MediQuery AI

## 🎯 Execution Strategy

This document outlines the detailed implementation plan for building the MediQuery AI system.

---

## 📋 Development Phases

### **Phase 0: Debug Infrastructure Setup** ⏱️ 2 hours

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

class DebugConfig(BaseSettings):
    """Global debug and tracing configuration"""
    DEBUG_MODE: bool = True
    LOG_LEVEL: LogLevel = LogLevel.DEBUG
    LOG_FORMAT: str = "json"
    TRACE_AGENTS: bool = True
    TRACE_LLM_CALLS: bool = True
    ENABLE_XRAY: bool = True
    
    class Config:
        env_file = ".env"

debug_config = DebugConfig()
```

#### 0.2 Structured Logging
**File**: `backend/app/utils/logger.py`

```python
import structlog
import logging
from app.config import debug_config

def setup_logging():
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer() if debug_config.LOG_FORMAT == "json"
            else structlog.dev.ConsoleRenderer()
        ],
        logger_factory=structlog.PrintLoggerFactory(),
    )
    return structlog.get_logger()

logger = setup_logging()
```

#### 0.3 Agent Tracer
**File**: `backend/app/utils/tracing.py`

```python
import time
import functools
from app.utils.logger import logger
from app.config import debug_config

class AgentTracer:
    def trace_agent(self, agent_name: str):
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(state: dict, *args, **kwargs):
                start_time = time.time()
                
                logger.info(f"🤖 Agent Started: {agent_name}", agent=agent_name)
                
                try:
                    result = await func(state, *args, **kwargs)
                    duration_ms = (time.time() - start_time) * 1000
                    
                    logger.info(
                        f"⏱️  Agent Completed: {agent_name}",
                        agent=agent_name,
                        duration_ms=round(duration_ms, 2),
                        status="success"
                    )
                    
                    if 'agent_trace' not in result:
                        result['agent_trace'] = []
                    result['agent_trace'].append({
                        'agent': agent_name,
                        'duration_ms': round(duration_ms, 2),
                        'status': 'success'
                    })
                    
                    return result
                except Exception as e:
                    logger.error(f"❌ Agent Failed: {agent_name}", error=str(e))
                    raise
            return wrapper
        return decorator

tracer = AgentTracer()
```

---

### **Phase 1: Project Setup & Foundation** ⏱️ 4 hours

#### 1.1 Project Structure
```
IndegeneProject/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app
│   │   ├── config.py               # Settings
│   │   ├── models/                 # Pydantic models
│   │   ├── agents/                 # LangGraph agents
│   │   │   ├── __init__.py
│   │   │   ├── document_processor.py
│   │   │   ├── query_analyzer.py
│   │   │   ├── retrieval.py
│   │   │   ├── reranking.py
│   │   │   └── synthesis.py
│   │   ├── services/               # Business logic
│   │   │   ├── opensearch.py
│   │   │   ├── bedrock.py
│   │   │   ├── s3.py
│   │   │   └── embeddings.py
│   │   ├── api/                    # API routes
│   │   │   ├── upload.py
│   │   │   ├── query.py
│   │   │   └── documents.py
│   │   └── utils/                  # Utilities
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
├── infrastructure/
│   ├── cdk/                        # AWS CDK
│   └── terraform/                  # Alternative
├── docs/
├── .windsurf/
│   └── knowledge/
└── README.md
```

#### 1.2 Dependencies Installation
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

#### 1.3 Environment Configuration
```bash
# .env file
AWS_REGION=us-east-1
AWS_PROFILE=default
OPENSEARCH_ENDPOINT=
S3_BUCKET=mediquery-documents
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
LOG_LEVEL=INFO
```

---

### **Phase 2: Backend Core Development** ⏱️ 12 hours

#### 2.1 FastAPI Application Setup
**File**: `backend/app/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import upload, query, documents
from app.config import settings

app = FastAPI(
    title="MediQuery AI",
    version="1.0.0",
    description="Clinical Document Intelligence Platform"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(upload.router, prefix="/api/v1", tags=["upload"])
app.include_router(query.router, prefix="/api/v1", tags=["query"])
app.include_router(documents.router, prefix="/api/v1", tags=["documents"])

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

#### 2.2 Configuration Management
**File**: `backend/app/config.py`

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # AWS
    aws_region: str = "us-east-1"
    s3_bucket: str
    opensearch_endpoint: str
    bedrock_model_id: str = "anthropic.claude-sonnet-4-6-20260223-v1:0"  # Claude Sonnet 4.6
    
    # Application
    log_level: str = "INFO"
    max_file_size: int = 52428800  # 50MB
    chunk_size: int = 512
    chunk_overlap: int = 50
    
    # Vector Search
    embedding_model: str = "BAAI/bge-large-en-v1.5"
    embedding_dimension: int = 1024
    top_k: int = 20
    rerank_top_k: int = 5
    
    class Config:
        env_file = ".env"

settings = Settings()
```

#### 2.3 Service Layer Implementation

**File**: `backend/app/services/embeddings.py`
```python
from sentence_transformers import SentenceTransformer
from typing import List
import asyncio

class EmbeddingService:
    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name)
    
    async def encode(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings asynchronously"""
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(
            None,
            self.model.encode,
            texts,
            32,  # batch_size
            True,  # show_progress_bar
            True   # normalize_embeddings
        )
        return embeddings.tolist()

# Global instance
embedding_service = EmbeddingService(settings.embedding_model)
```

**File**: `backend/app/services/opensearch.py`
```python
from opensearchpy import OpenSearch, AsyncOpenSearch
from typing import List, Dict
import asyncio

class OpenSearchService:
    def __init__(self, endpoint: str):
        self.client = AsyncOpenSearch(
            hosts=[endpoint],
            http_auth=('admin', 'password'),  # Use Secrets Manager
            use_ssl=True,
            verify_certs=True,
            ssl_show_warn=False
        )
    
    async def create_index(self, index_name: str):
        """Create index with vector field"""
        body = {
            "settings": {
                "index.knn": True,
                "number_of_shards": 3,
                "number_of_replicas": 2
            },
            "mappings": {
                "properties": {
                    "text": {"type": "text"},
                    "embedding": {
                        "type": "knn_vector",
                        "dimension": 1024,
                        "method": {
                            "name": "hnsw",
                            "space_type": "cosinesimil",
                            "engine": "nmslib"
                        }
                    },
                    "metadata": {"type": "object"}
                }
            }
        }
        await self.client.indices.create(index=index_name, body=body)
    
    async def hybrid_search(
        self, 
        index: str, 
        query_text: str, 
        query_embedding: List[float],
        top_k: int = 20
    ) -> List[Dict]:
        """Hybrid search (semantic + keyword)"""
        body = {
            "size": top_k,
            "query": {
                "hybrid": {
                    "queries": [
                        {
                            "knn": {
                                "embedding": {
                                    "vector": query_embedding,
                                    "k": top_k
                                }
                            }
                        },
                        {
                            "match": {
                                "text": query_text
                            }
                        }
                    ]
                }
            }
        }
        
        response = await self.client.search(index=index, body=body)
        return [hit["_source"] for hit in response["hits"]["hits"]]

opensearch_service = OpenSearchService(settings.opensearch_endpoint)
```

**File**: `backend/app/services/bedrock.py`
```python
import boto3
import json
import time
from typing import AsyncGenerator
from app.utils.logger import logger
from app.utils.llm_tracer import llm_tracer

class BedrockService:
    def __init__(self, model_id: str, region: str):
        self.client = boto3.client(
            'bedrock-runtime',
            region_name=region
        )
        # Claude Sonnet 4.6 - Latest 2026 model with improved reasoning
        self.model_id = model_id or "anthropic.claude-sonnet-4-6-20260223-v1:0"
        
        logger.info(
            "Bedrock service initialized",
            model_id=self.model_id,
            region=region
        )
    
    async def invoke(
        self, 
        prompt: str, 
        max_tokens: int = 1000,
        temperature: float = 0.1,
        trace_id: str = None
    ) -> str:
        """Invoke Claude Sonnet 4.6 model with tracing"""
        start_time = time.time()
        
        logger.debug("Invoking Bedrock", model=self.model_id, prompt_length=len(prompt))
        
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body)
        )
        
        result = json.loads(response['body'].read())
        answer = result['content'][0]['text']
        
        # Calculate tokens (approximate)
        tokens_input = len(prompt) // 4
        tokens_output = len(answer) // 4
        duration_ms = (time.time() - start_time) * 1000
        
        # Trace LLM call
        await llm_tracer.trace_llm_call(
            model_id=self.model_id,
            prompt=prompt,
            response=answer,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            duration_ms=duration_ms,
            trace_id=trace_id or "unknown"
        )
        
        return answer
    
    async def stream(
        self, 
        prompt: str, 
        max_tokens: int = 1000
    ) -> AsyncGenerator[str, None]:
        """Stream Claude responses"""
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.1
        }
        
        response = self.client.invoke_model_with_response_stream(
            modelId=self.model_id,
            body=json.dumps(body)
        )
        
        for event in response['body']:
            chunk = json.loads(event['chunk']['bytes'])
            if chunk['type'] == 'content_block_delta':
                yield chunk['delta']['text']

bedrock_service = BedrockService(
    settings.bedrock_model_id,
    settings.aws_region
)
```

**File**: `backend/app/utils/llm_tracer.py`
```python
from app.utils.logger import logger
from app.config import debug_config

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
        if debug_config.TRACE_LLM_CALLS:
            logger.info(
                "🧠 LLM Call",
                model=model_id,
                trace_id=trace_id,
                tokens_input=tokens_input,
                tokens_output=tokens_output,
                duration_ms=round(duration_ms, 2),
                cost_usd=LLMTracer._estimate_cost(model_id, tokens_input, tokens_output)
            )
        
        if debug_config.TRACE_LLM_PROMPTS:
            logger.debug("📝 LLM Prompt", prompt=prompt[:500])
        
        if debug_config.TRACE_LLM_RESPONSES:
            logger.debug("💬 LLM Response", response=response[:500])
    
    @staticmethod
    def _estimate_cost(model_id: str, tokens_input: int, tokens_output: int) -> float:
        # Claude Sonnet 4.6 pricing
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

#### 2.4 LangGraph Multi-Agent System

**File**: `backend/app/agents/graph.py`
```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Annotated
from operator import add

class AgentState(TypedDict):
    """Shared state across agents"""
    request_id: str
    user_query: str
    document_id: str
    intent: str
    search_strategy: str
    retrieved_chunks: List[Dict]
    reranked_chunks: List[Dict]
    final_answer: str
    citations: List[Dict]
    agent_trace: Annotated[List[Dict], add]
    errors: List[str]

def create_agent_graph():
    """Create LangGraph workflow"""
    from app.agents.query_analyzer import query_analyzer_agent
    from app.agents.retrieval import retrieval_agent
    from app.agents.reranking import reranking_agent
    from app.agents.synthesis import synthesis_agent
    
    graph = StateGraph(AgentState)
    
    # Add nodes
    graph.add_node("query_analyzer", query_analyzer_agent)
    graph.add_node("retrieval", retrieval_agent)
    graph.add_node("reranking", reranking_agent)
    graph.add_node("synthesis", synthesis_agent)
    
    # Add edges
    graph.set_entry_point("query_analyzer")
    graph.add_edge("query_analyzer", "retrieval")
    graph.add_edge("retrieval", "reranking")
    graph.add_edge("reranking", "synthesis")
    graph.add_edge("synthesis", END)
    
    return graph.compile()

agent_graph = create_agent_graph()
```

**File**: `backend/app/agents/query_analyzer.py`
```python
from app.agents.graph import AgentState
import time

async def query_analyzer_agent(state: AgentState) -> AgentState:
    """Analyze query and determine strategy"""
    start_time = time.time()
    
    # Simple intent classification (can use LLM for complex cases)
    query_lower = state['user_query'].lower()
    
    if any(word in query_lower for word in ['what', 'define', 'explain']):
        intent = 'factual_lookup'
        strategy = 'hybrid'
    elif any(word in query_lower for word in ['compare', 'difference', 'versus']):
        intent = 'comparison'
        strategy = 'semantic'
    else:
        intent = 'general_query'
        strategy = 'hybrid'
    
    state['intent'] = intent
    state['search_strategy'] = strategy
    state['agent_trace'].append({
        'agent': 'QueryAnalyzerAgent',
        'duration_ms': (time.time() - start_time) * 1000,
        'output': {'intent': intent, 'strategy': strategy}
    })
    
    return state
```

**File**: `backend/app/agents/retrieval.py`
```python
from app.agents.graph import AgentState
from app.services.opensearch import opensearch_service
from app.services.embeddings import embedding_service
import time

async def retrieval_agent(state: AgentState) -> AgentState:
    """Retrieve relevant chunks"""
    start_time = time.time()
    
    # Generate query embedding
    query_embedding = await embedding_service.encode([state['user_query']])
    
    # Hybrid search
    chunks = await opensearch_service.hybrid_search(
        index=f"medical-docs-{state['document_id']}",
        query_text=state['user_query'],
        query_embedding=query_embedding[0],
        top_k=20
    )
    
    state['retrieved_chunks'] = chunks
    state['agent_trace'].append({
        'agent': 'RetrievalAgent',
        'duration_ms': (time.time() - start_time) * 1000,
        'output': {'chunks_retrieved': len(chunks)}
    })
    
    return state
```

**File**: `backend/app/agents/reranking.py`
```python
from app.agents.graph import AgentState
from sentence_transformers import CrossEncoder
import time

reranker = CrossEncoder('BAAI/bge-reranker-large')

async def reranking_agent(state: AgentState) -> AgentState:
    """Rerank chunks using cross-encoder"""
    start_time = time.time()
    
    # Prepare pairs
    pairs = [
        (state['user_query'], chunk['text'])
        for chunk in state['retrieved_chunks']
    ]
    
    # Score
    scores = reranker.predict(pairs)
    
    # Sort and select top-k
    ranked = sorted(
        zip(state['retrieved_chunks'], scores),
        key=lambda x: x[1],
        reverse=True
    )
    
    state['reranked_chunks'] = [chunk for chunk, _ in ranked[:5]]
    state['agent_trace'].append({
        'agent': 'RerankingAgent',
        'duration_ms': (time.time() - start_time) * 1000,
        'output': {'chunks_selected': 5}
    })
    
    return state
```

**File**: `backend/app/agents/synthesis.py`
```python
from app.agents.graph import AgentState
from app.services.bedrock import bedrock_service
from app.utils.tracing import tracer
from app.utils.logger import logger
import time

@tracer.trace_agent("SynthesisAgent")
async def synthesis_agent(state: AgentState) -> AgentState:
    """Generate final answer with citations"""
    start_time = time.time()
    
    # Build context
    context = "\n\n".join([
        f"[Source {i+1}] {chunk['text']}\n"
        f"(From: {chunk['metadata']['source']}, Page: {chunk['metadata']['page']})"
        for i, chunk in enumerate(state['reranked_chunks'])
    ])
    
    # Prompt
    prompt = f"""You are a medical information assistant. Answer the question using ONLY the provided context.

Context:
{context}

Question: {state['user_query']}

Instructions:
1. Answer based solely on the context
2. Cite sources using [Source N] format
3. If context is insufficient, say so
4. Use medical terminology appropriately
"""
    
    # Call Bedrock with tracing
    logger.debug("Calling Claude Sonnet 4.6 for synthesis")
    answer = await bedrock_service.invoke(
        prompt, 
        max_tokens=1000,
        trace_id=state.get('request_id')
    )
    
    state['final_answer'] = answer
    state['citations'] = [
        {
            'source': chunk['metadata']['source'],
            'page': chunk['metadata']['page'],
            'text': chunk['text'][:200]
        }
        for chunk in state['reranked_chunks']
    ]
    state['agent_trace'].append({
        'agent': 'SynthesisAgent',
        'duration_ms': (time.time() - start_time) * 1000,
        'output': {'answer_length': len(answer)}
    })
    
    return state
```

#### 2.5 API Routes

**File**: `backend/app/api/query.py`
```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.agents.graph import agent_graph, AgentState
import uuid

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    document_id: str

class QueryResponse(BaseModel):
    answer: str
    citations: list
    confidence: float
    processing_time: float
    agent_trace: list

@router.post("/query", response_model=QueryResponse)
async def query_document(request: QueryRequest):
    """Process user query"""
    import time
    start_time = time.time()
    
    # Initialize state
    initial_state: AgentState = {
        'request_id': str(uuid.uuid4()),
        'user_query': request.query,
        'document_id': request.document_id,
        'intent': '',
        'search_strategy': '',
        'retrieved_chunks': [],
        'reranked_chunks': [],
        'final_answer': '',
        'citations': [],
        'agent_trace': [],
        'errors': []
    }
    
    # Run agent graph
    result = await agent_graph.ainvoke(initial_state)
    
    return QueryResponse(
        answer=result['final_answer'],
        citations=result['citations'],
        confidence=0.85,  # TODO: Calculate actual confidence
        processing_time=time.time() - start_time,
        agent_trace=result['agent_trace']
    )
```

---

### **Phase 3: Frontend Development** ⏱️ 8 hours

#### 3.1 React Setup with Vite
```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
npm install @tanstack/react-query axios lucide-react
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

#### 3.2 Main Components

**File**: `frontend/src/components/QueryInterface.tsx`
```typescript
import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import axios from 'axios';

export function QueryInterface({ documentId }: { documentId: string }) {
  const [query, setQuery] = useState('');
  
  const queryMutation = useMutation({
    mutationFn: async (query: string) => {
      const response = await axios.post('/api/v1/query', {
        query,
        document_id: documentId
      });
      return response.data;
    }
  });
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    queryMutation.mutate(query);
  };
  
  return (
    <div className="space-y-4">
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask a question..."
          className="w-full p-3 border rounded-lg"
        />
        <button type="submit" className="mt-2 px-4 py-2 bg-blue-600 text-white rounded">
          Ask
        </button>
      </form>
      
      {queryMutation.data && (
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="font-bold mb-2">Answer:</h3>
          <p>{queryMutation.data.answer}</p>
          
          <h4 className="font-bold mt-4 mb-2">Citations:</h4>
          <ul className="space-y-2">
            {queryMutation.data.citations.map((citation, i) => (
              <li key={i} className="text-sm text-gray-600">
                {citation.source}, Page {citation.page}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
```

---

### **Phase 4: AWS Deployment** ⏱️ 8 hours

#### 4.1 Infrastructure as Code (AWS CDK)

**File**: `infrastructure/cdk/lib/mediquery-stack.ts`
```typescript
import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigateway from 'aws-cdk-lib/aws-apigatewayv2';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as opensearch from 'aws-cdk-lib/aws-opensearchservice';

export class MediQueryStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
    super(scope, id, props);
    
    // S3 Bucket
    const documentBucket = new s3.Bucket(this, 'DocumentBucket', {
      encryption: s3.BucketEncryption.KMS,
      versioned: true,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL
    });
    
    // Lambda Function
    const apiFunction = new lambda.Function(this, 'ApiFunction', {
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'app.main.handler',
      code: lambda.Code.fromAsset('../backend'),
      memorySize: 3008,
      timeout: cdk.Duration.minutes(15),
      environment: {
        S3_BUCKET: documentBucket.bucketName,
        OPENSEARCH_ENDPOINT: opensearchDomain.domainEndpoint
      }
    });
    
    // API Gateway
    const httpApi = new apigateway.HttpApi(this, 'HttpApi', {
      defaultIntegration: new apigateway.HttpLambdaIntegration(
        'ApiIntegration',
        apiFunction
      )
    });
  }
}
```

---

### **Phase 5: Testing & Documentation** ⏱️ 4 hours

#### 5.1 Unit Tests
```python
# tests/test_agents.py
import pytest
from app.agents.query_analyzer import query_analyzer_agent

@pytest.mark.asyncio
async def test_query_analyzer():
    state = {
        'user_query': 'What are the side effects?',
        'agent_trace': []
    }
    result = await query_analyzer_agent(state)
    assert result['intent'] == 'factual_lookup'
```

#### 5.2 Integration Tests
```python
# tests/test_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
```

---

## 🎯 Success Metrics

- [ ] All unit tests passing (>80% coverage)
- [ ] Integration tests passing
- [ ] API response time < 3s (p95)
- [ ] Successfully deployed to AWS
- [ ] Documentation complete
- [ ] Demo script prepared

---

**Plan Version**: 1.0  
**Created**: March 5, 2026  
**Estimated Total Time**: 36 hours (6 days @ 6 hours/day)
