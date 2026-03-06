# System Architecture - MediQuery AI

## 🏗️ Complete Architecture Design

This document provides a comprehensive view of the system architecture, component interactions, and design decisions.

---

## 📐 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER LAYER                                     │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │              React Frontend (Vite + TailwindCSS)                 │  │
│  │  - Document Upload UI                                            │  │
│  │  - Chat Interface                                                │  │
│  │  - Citation Viewer                                               │  │
│  │  - Agent Activity Monitor                                        │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │ HTTPS
                                 │
┌────────────────────────────────▼────────────────────────────────────────┐
│                          AWS CLOUD (VPC)                                 │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    AWS API Gateway (HTTP API)                    │  │
│  │  - Rate limiting                                                 │  │
│  │  - Authentication (Cognito/API Key)                              │  │
│  │  - Request/Response transformation                               │  │
│  └────────────────────────────┬─────────────────────────────────────┘  │
│                                │                                         │
│  ┌────────────────────────────▼─────────────────────────────────────┐  │
│  │              AWS Lambda (FastAPI Application)                    │  │
│  │  ┌──────────────────────────────────────────────────────────┐   │  │
│  │  │                  FastAPI Router                          │   │  │
│  │  │  - /upload (POST)                                        │   │  │
│  │  │  - /query (POST)                                         │   │  │
│  │  │  - /documents (GET)                                      │   │  │
│  │  │  - /health (GET)                                         │   │  │
│  │  └────────────────────────┬─────────────────────────────────┘   │  │
│  │                            │                                     │  │
│  │  ┌────────────────────────▼─────────────────────────────────┐   │  │
│  │  │         LangGraph Orchestrator (State Machine)           │   │  │
│  │  │                                                           │   │  │
│  │  │  ┌─────────────────────────────────────────────────┐     │   │  │
│  │  │  │           StateGraph Definition                 │     │   │  │
│  │  │  │                                                  │     │   │  │
│  │  │  │  START                                           │     │   │  │
│  │  │  │    ↓                                             │     │   │  │
│  │  │  │  [Route Decision]                                │     │   │  │
│  │  │  │    ├─→ Document Upload Path                      │     │   │  │
│  │  │  │    │     ↓                                        │     │   │  │
│  │  │  │    │   DocumentProcessorAgent                     │     │   │  │
│  │  │  │    │     ↓                                        │     │   │  │
│  │  │  │    │   EmbeddingAgent                             │     │   │  │
│  │  │  │    │     ↓                                        │     │   │  │
│  │  │  │    │   VectorStoreAgent                           │     │   │  │
│  │  │  │    │                                              │     │   │  │
│  │  │  │    └─→ Query Path                                 │     │   │  │
│  │  │  │          ↓                                        │     │   │  │
│  │  │  │        QueryAnalyzerAgent                         │     │   │  │
│  │  │  │          ↓                                        │     │   │  │
│  │  │  │        RetrievalAgent                             │     │   │  │
│  │  │  │          ↓                                        │     │   │  │
│  │  │  │        RerankingAgent                             │     │   │  │
│  │  │  │          ↓                                        │     │   │  │
│  │  │  │        SynthesisAgent                             │     │   │  │
│  │  │  │          ↓                                        │     │   │  │
│  │  │  │        END                                        │     │   │  │
│  │  │  └─────────────────────────────────────────────────┘     │   │  │
│  │  └───────────────────────────────────────────────────────────┘   │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    Integration Services                          │  │
│  │                                                                   │  │
│  │  ┌─────────────────┐  ┌──────────────────┐  ┌────────────────┐  │  │
│  │  │  Amazon Bedrock │  │  HuggingFace     │  │  OpenSearch    │  │  │
│  │  │  (VPC Endpoint) │  │  Embeddings      │  │  (Vector DB)   │  │  │
│  │  │                 │  │  (Self-hosted)   │  │                │  │  │
│  │  │  Claude 3.5     │  │  bge-large-en    │  │  k-NN Index    │  │  │
│  │  │  Sonnet         │  │  (EKS Pod)       │  │  BM25 Index    │  │  │
│  │  └─────────────────┘  └──────────────────┘  └────────────────┘  │  │
│  │                                                                   │  │
│  │  ┌─────────────────┐  ┌──────────────────┐  ┌────────────────┐  │  │
│  │  │  AWS S3         │  │  CloudWatch      │  │  CloudTrail    │  │  │
│  │  │  (Documents)    │  │  (Logs/Metrics)  │  │  (Audit)       │  │  │
│  │  │                 │  │                  │  │                │  │  │
│  │  │  - Raw PDFs     │  │  - API Logs      │  │  - API Calls   │  │  │
│  │  │  - Processed    │  │  - Agent Traces  │  │  - S3 Access   │  │  │
│  │  │  - Metadata     │  │  - Errors        │  │  - Bedrock Use │  │  │
│  │  └─────────────────┘  └──────────────────┘  └────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🤖 Multi-Agent System Design

### **Agent Architecture (LangGraph)**

```python
# State Definition
class AgentState(TypedDict):
    """Shared state across all agents"""
    request_id: str
    user_query: str
    document_id: Optional[str]
    intent: str
    search_strategy: str
    retrieved_chunks: List[Dict]
    reranked_chunks: List[Dict]
    final_answer: str
    citations: List[Dict]
    metadata: Dict
    errors: List[str]

# Agent Graph
graph = StateGraph(AgentState)

# Add nodes (agents)
graph.add_node("query_analyzer", query_analyzer_agent)
graph.add_node("retrieval", retrieval_agent)
graph.add_node("reranking", reranking_agent)
graph.add_node("synthesis", synthesis_agent)

# Add edges (workflow)
graph.add_edge(START, "query_analyzer")
graph.add_conditional_edges(
    "query_analyzer",
    route_based_on_intent,
    {
        "simple_lookup": "retrieval",
        "complex_analysis": "retrieval",
        "comparison": "retrieval"
    }
)
graph.add_edge("retrieval", "reranking")
graph.add_edge("reranking", "synthesis")
graph.add_edge("synthesis", END)
```

### **Agent Responsibilities**

#### **1. QueryAnalyzerAgent**
**Purpose**: Understand user intent and plan retrieval strategy

**Inputs**:
- User query (natural language)
- Conversation history (optional)

**Outputs**:
- Intent classification (lookup/analysis/comparison)
- Search strategy (semantic/keyword/hybrid)
- Query expansion terms
- Confidence score

**Implementation**:
```python
async def query_analyzer_agent(state: AgentState) -> AgentState:
    """Analyze query and determine retrieval strategy"""
    
    # Use lightweight LLM for classification
    prompt = f"""
    Analyze this medical query and classify:
    Query: {state['user_query']}
    
    Classify intent:
    - factual_lookup: Simple fact retrieval
    - complex_analysis: Requires reasoning
    - comparison: Comparing multiple entities
    
    Suggest search strategy:
    - semantic: Meaning-based search
    - keyword: Exact term matching
    - hybrid: Both semantic + keyword
    """
    
    result = await bedrock_client.invoke(prompt)
    
    state['intent'] = result.intent
    state['search_strategy'] = result.strategy
    return state
```

#### **2. RetrievalAgent**
**Purpose**: Fetch relevant document chunks from vector database

**Inputs**:
- Query (original or expanded)
- Search strategy
- Filters (document type, date range)

**Outputs**:
- Top-k chunks (default k=20)
- Similarity scores
- Metadata (source, page, section)

**Implementation**:
```python
async def retrieval_agent(state: AgentState) -> AgentState:
    """Retrieve relevant chunks from OpenSearch"""
    
    # Generate query embedding
    query_embedding = await embedding_model.encode(
        state['user_query']
    )
    
    # Hybrid search
    if state['search_strategy'] == 'hybrid':
        # Semantic search (k-NN)
        semantic_results = await opensearch_client.search(
            index="medical_documents",
            body={
                "query": {
                    "knn": {
                        "embedding": {
                            "vector": query_embedding,
                            "k": 10
                        }
                    }
                }
            }
        )
        
        # Keyword search (BM25)
        keyword_results = await opensearch_client.search(
            index="medical_documents",
            body={
                "query": {
                    "match": {
                        "text": state['user_query']
                    }
                }
            }
        )
        
        # Merge results (Reciprocal Rank Fusion)
        merged = merge_results(semantic_results, keyword_results)
        state['retrieved_chunks'] = merged[:20]
    
    return state
```

#### **3. RerankingAgent**
**Purpose**: Reorder chunks using cross-encoder for better relevance

**Inputs**:
- Retrieved chunks (top-20)
- Original query

**Outputs**:
- Reranked chunks (top-5)
- Relevance scores

**Implementation**:
```python
async def reranking_agent(state: AgentState) -> AgentState:
    """Rerank chunks using cross-encoder"""
    
    # Prepare pairs (query, chunk)
    pairs = [
        (state['user_query'], chunk['text'])
        for chunk in state['retrieved_chunks']
    ]
    
    # Score with cross-encoder
    scores = cross_encoder.predict(pairs)
    
    # Sort by score
    ranked = sorted(
        zip(state['retrieved_chunks'], scores),
        key=lambda x: x[1],
        reverse=True
    )
    
    state['reranked_chunks'] = [chunk for chunk, _ in ranked[:5]]
    return state
```

#### **4. SynthesisAgent**
**Purpose**: Generate final answer with citations using LLM

**Inputs**:
- Reranked chunks (context)
- Original query
- Intent

**Outputs**:
- Natural language answer
- Citations with source attribution
- Confidence score

**Implementation**:
```python
async def synthesis_agent(state: AgentState) -> AgentState:
    """Generate answer using Bedrock Claude"""
    
    # Build context from chunks
    context = "\n\n".join([
        f"[Source {i+1}] {chunk['text']}\n"
        f"(From: {chunk['source']}, Page: {chunk['page']})"
        for i, chunk in enumerate(state['reranked_chunks'])
    ])
    
    # Prompt engineering
    prompt = f"""
    You are a medical information assistant. Answer the question using ONLY 
    the provided context. Include citations.
    
    Context:
    {context}
    
    Question: {state['user_query']}
    
    Instructions:
    1. Answer based solely on the context
    2. Cite sources using [Source N] format
    3. If context is insufficient, say so
    4. Use medical terminology appropriately
    """
    
    # Call Bedrock
    response = await bedrock_client.invoke_model(
        modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
        body={
            "anthropic_version": "bedrock-2023-05-31",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1000,
            "temperature": 0.1
        }
    )
    
    state['final_answer'] = response['content'][0]['text']
    state['citations'] = extract_citations(response, state['reranked_chunks'])
    
    return state
```

#### **5. DocumentProcessorAgent**
**Purpose**: Process uploaded PDFs into searchable chunks

**Inputs**:
- PDF file (S3 path)
- Processing options

**Outputs**:
- Extracted text chunks
- Metadata (title, authors, sections)
- Embeddings

**Implementation**:
```python
async def document_processor_agent(state: AgentState) -> AgentState:
    """Process PDF and create chunks"""
    
    # Download from S3
    pdf_bytes = await s3_client.get_object(
        Bucket=BUCKET_NAME,
        Key=state['document_id']
    )
    
    # Extract text with layout
    from unstructured.partition.pdf import partition_pdf
    elements = partition_pdf(
        file=pdf_bytes,
        strategy="hi_res",
        extract_tables=True
    )
    
    # Intelligent chunking
    chunks = []
    current_chunk = []
    current_size = 0
    
    for element in elements:
        # Respect section boundaries
        if element.category == "Title":
            if current_chunk:
                chunks.append({
                    "text": "\n".join(current_chunk),
                    "metadata": {...}
                })
                current_chunk = []
        
        current_chunk.append(str(element))
        current_size += len(str(element))
        
        # Max chunk size: 512 tokens
        if current_size > 2000:  # ~512 tokens
            chunks.append({
                "text": "\n".join(current_chunk),
                "metadata": {...}
            })
            current_chunk = []
            current_size = 0
    
    state['chunks'] = chunks
    return state
```

---

## 🔄 Data Flow Examples

### **Example 1: Document Upload**

```
1. User uploads PDF via React UI
   ↓
2. Frontend → API Gateway → Lambda
   POST /upload
   Body: {file: <binary>, metadata: {...}}
   ↓
3. Lambda stores PDF in S3
   s3://mediquery-docs/raw/doc_123.pdf
   ↓
4. LangGraph triggers DocumentProcessorAgent
   State: {document_id: "doc_123", status: "processing"}
   ↓
5. DocumentProcessorAgent:
   - Downloads PDF from S3
   - Extracts text (Unstructured)
   - Creates chunks (512 tokens each)
   - Extracts metadata
   ↓
6. EmbeddingAgent:
   - Generates embeddings (bge-large-en-v1.5)
   - Batch size: 32 chunks at a time
   ↓
7. VectorStoreAgent:
   - Indexes in OpenSearch
   - Creates both k-NN and BM25 indices
   ↓
8. Response to user:
   {
     "document_id": "doc_123",
     "status": "indexed",
     "chunks": 47,
     "processing_time": 23.4
   }
```

### **Example 2: Query Processing**

```
1. User asks: "What are the primary endpoints?"
   ↓
2. Frontend → API Gateway → Lambda
   POST /query
   Body: {query: "...", document_id: "doc_123"}
   ↓
3. LangGraph StateGraph execution:
   
   QueryAnalyzerAgent:
   - Intent: "factual_lookup"
   - Strategy: "hybrid"
   - Confidence: 0.92
   ↓
   RetrievalAgent:
   - Semantic search: 10 results
   - Keyword search: 10 results
   - Merged (RRF): 20 unique chunks
   ↓
   RerankingAgent:
   - Cross-encoder scores all 20
   - Selects top 5 (scores > 0.7)
   ↓
   SynthesisAgent:
   - Builds context from top 5 chunks
   - Calls Bedrock Claude 3.5 Sonnet
   - Generates answer with citations
   ↓
4. Response to user:
   {
     "answer": "The primary endpoints are:\n1. Overall Survival...",
     "citations": [
       {"source": "doc_123", "page": 12, "chunk_id": "..."},
       ...
     ],
     "confidence": 0.89,
     "processing_time": 2.3
   }
```

---

## 🔐 Security Architecture

### **Network Security**

```
┌─────────────────────────────────────────────┐
│              Public Internet                 │
└────────────────┬────────────────────────────┘
                 │ HTTPS (TLS 1.3)
                 │
┌────────────────▼────────────────────────────┐
│          CloudFront (CDN)                    │
│  - DDoS protection                           │
│  - WAF rules                                 │
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│         API Gateway (VPC Link)               │
│  - Rate limiting: 100 req/min               │
│  - API key validation                        │
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│              Private VPC                     │
│  ┌──────────────────────────────────────┐   │
│  │  Lambda (Private Subnet)             │   │
│  │  - No internet access                │   │
│  │  - VPC endpoints only                │   │
│  └──────────────────────────────────────┘   │
│                                              │
│  ┌──────────────────────────────────────┐   │
│  │  VPC Endpoints                       │   │
│  │  - Bedrock                           │   │
│  │  - S3                                │   │
│  │  - OpenSearch                        │   │
│  └──────────────────────────────────────┘   │
└──────────────────────────────────────────────┘
```

### **Data Encryption**

**At Rest**:
- S3: AES-256 with KMS (customer-managed keys)
- OpenSearch: Encryption enabled
- Lambda environment variables: KMS encrypted

**In Transit**:
- TLS 1.3 for all API calls
- VPC endpoints (no internet routing)
- Bedrock: AWS PrivateLink

### **Access Control**

**IAM Roles**:
```yaml
LambdaExecutionRole:
  Policies:
    - S3ReadWrite: mediquery-docs/*
    - BedrockInvoke: claude-3-5-sonnet
    - OpenSearchAccess: mediquery-index
    - CloudWatchLogs: /aws/lambda/mediquery
    - KMSDecrypt: customer-managed-key
```

**API Authentication**:
- Option 1: AWS Cognito (user pools)
- Option 2: API Keys (for demo)
- Option 3: IAM authentication

---

## 📊 Performance Optimization

### **Caching Strategy**

```python
# Multi-level caching
L1_CACHE = {}  # In-memory (Lambda)
L2_CACHE = "ElastiCache Redis"  # Distributed

async def get_embeddings(text: str):
    # L1 cache check
    cache_key = hash(text)
    if cache_key in L1_CACHE:
        return L1_CACHE[cache_key]
    
    # L2 cache check
    cached = await redis.get(f"emb:{cache_key}")
    if cached:
        L1_CACHE[cache_key] = cached
        return cached
    
    # Generate embedding
    embedding = await model.encode(text)
    
    # Store in both caches
    L1_CACHE[cache_key] = embedding
    await redis.setex(f"emb:{cache_key}", 3600, embedding)
    
    return embedding
```

### **Batch Processing**

```python
# Process documents in batches
async def batch_embed_chunks(chunks: List[str]):
    """Embed chunks in batches for efficiency"""
    batch_size = 32
    embeddings = []
    
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        batch_embeddings = await model.encode(batch)
        embeddings.extend(batch_embeddings)
    
    return embeddings
```

### **Connection Pooling**

```python
# Reuse connections across Lambda invocations
opensearch_client = OpenSearch(
    hosts=[OPENSEARCH_ENDPOINT],
    pool_maxsize=20,
    timeout=30
)

bedrock_client = boto3.client(
    'bedrock-runtime',
    config=Config(
        max_pool_connections=50,
        retries={'max_attempts': 3}
    )
)
```

---

## 🎯 Scalability Design

### **Horizontal Scaling**

```
API Gateway
    ↓
Lambda (Auto-scaling)
├─ Concurrent executions: 1000
├─ Reserved concurrency: 100 (for critical paths)
└─ Provisioned concurrency: 10 (warm starts)

OpenSearch
├─ Data nodes: 3 (r6g.xlarge)
├─ Master nodes: 3 (c6g.large)
└─ Auto-scaling: CPU > 70%

S3
└─ Unlimited (managed by AWS)
```

### **Load Testing Targets**

```yaml
Performance_SLAs:
  p50_latency: < 1.5s
  p95_latency: < 3.0s
  p99_latency: < 5.0s
  throughput: 50 queries/sec
  availability: 99.9%
```

---

## 🔍 Monitoring & Observability

### **Metrics Tracked**

```python
# CloudWatch Custom Metrics
metrics = {
    "QueryLatency": "Milliseconds",
    "RetrievalAccuracy": "Percent",
    "ChunkRelevance": "Score",
    "BedrockTokens": "Count",
    "OpenSearchLatency": "Milliseconds",
    "CacheHitRate": "Percent",
    "ErrorRate": "Count"
}
```

### **Logging Strategy**

```python
import structlog

logger = structlog.get_logger()

logger.info(
    "query_processed",
    request_id=request_id,
    query=query,
    intent=intent,
    chunks_retrieved=len(chunks),
    latency_ms=latency,
    bedrock_tokens=tokens
)
```

### **Distributed Tracing**

```python
# AWS X-Ray integration
from aws_xray_sdk.core import xray_recorder

@xray_recorder.capture('query_processing')
async def process_query(query: str):
    with xray_recorder.capture('retrieval'):
        chunks = await retrieve(query)
    
    with xray_recorder.capture('synthesis'):
        answer = await synthesize(chunks)
    
    return answer
```

---

## 🚀 Deployment Architecture

### **Environment Strategy**

```
Development
├─ Local: Docker Compose
├─ AWS: dev account
└─ Features: Debug logging, no rate limits

Staging
├─ AWS: staging account
├─ Features: Production-like, test data
└─ Purpose: Integration testing

Production
├─ AWS: prod account
├─ Features: Full monitoring, backups
└─ Purpose: Live traffic
```

### **CI/CD Pipeline**

```yaml
# GitHub Actions
on: [push, pull_request]

jobs:
  test:
    - Run unit tests
    - Run integration tests
    - Check code coverage (>80%)
  
  build:
    - Build Docker image
    - Push to ECR
  
  deploy:
    - Deploy to staging (on merge to main)
    - Run smoke tests
    - Deploy to production (on tag)
```

---

**Architecture Version**: 1.0  
**Last Updated**: March 5, 2026  
**Next Review**: Before production deployment
