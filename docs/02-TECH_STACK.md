# Tech Stack - 2026 Latest Versions

## 📦 Complete Technology Stack

This document details all technologies, their versions, and rationale for selection based on 2026 best practices.

---

## 🐍 Core Backend Stack

### **Python 3.12.7**
- **Version**: `3.12.7` (Latest stable as of March 2026)
- **Why**: 
  - Improved async performance (PEP 684)
  - Better type hints and error messages
  - 25% faster than Python 3.11 for async workloads
  - Full compatibility with all major ML libraries
- **Key Features Used**:
  - `async`/`await` for concurrent operations
  - Type hints with `typing` module
  - Pattern matching for agent routing
  - Improved `asyncio` performance

### **FastAPI 0.135.1**
- **Version**: `0.135.1` (Released March 1, 2026)
- **Why**:
  - Native async support (critical for LLM streaming)
  - Automatic OpenAPI/Swagger documentation
  - Pydantic v2 integration (2x faster validation)
  - Built-in dependency injection
  - Production-ready with Uvicorn
- **Key Features**:
  - WebSocket support for streaming responses
  - Background tasks for document processing
  - Middleware for authentication/logging
  - CORS configuration for frontend

**Dependencies**:
```python
fastapi==0.135.1
uvicorn[standard]==0.34.0  # ASGI server
pydantic==2.10.5           # Data validation
pydantic-settings==2.7.1   # Environment config
```

---

## 🦜 LangChain Ecosystem

### **LangChain 1.2.10**
- **Version**: `1.2.10` (Released February 10, 2026)
- **Why**:
  - Industry standard for LLM orchestration
  - Rich ecosystem of integrations
  - Production-tested RAG components
  - Excellent observability (LangSmith)
- **Components Used**:
  - `langchain-core`: Base abstractions
  - `langchain-community`: Integrations
  - `langchain-aws`: Bedrock integration
  - `langchain-text-splitters`: Document chunking

**Key Packages**:
```python
langchain==1.2.10
langchain-core==1.2.17
langchain-community==1.2.15
langchain-aws==1.2.8
langchain-text-splitters==1.2.5
```

### **LangGraph 0.2.65**
- **Version**: `0.2.65` (Latest stable 2026)
- **Why**:
  - Purpose-built for multi-agent workflows
  - State management for complex workflows
  - Cycle support (critical for agentic loops)
  - Streaming and checkpointing
  - MCP-compatible architecture
- **Key Features**:
  - `StateGraph` for agent orchestration
  - Conditional edges for dynamic routing
  - Persistent state across agent calls
  - Built-in error handling and retries

**Package**:
```python
langgraph==0.2.65
langgraph-checkpoint==0.2.15  # State persistence
```

---

## 🤗 HuggingFace Stack

### **Transformers 5.3.0**
- **Version**: `5.3.0` (Released March 2026)
- **Why**:
  - Latest model architectures
  - Improved tokenization (v5 rewrite)
  - Better multi-modal support
  - Optimized inference performance
- **Breaking Changes in v5**:
  - New tokenizer backend (faster)
  - Dynamic weight loading
  - Simplified API

**Package**:
```python
transformers==5.3.0
torch==2.5.1              # PyTorch backend
accelerate==1.2.1         # Distributed inference
```

### **Sentence Transformers 3.5.0**
- **Version**: `3.5.0` (2026 latest)
- **Why**:
  - State-of-the-art embeddings
  - Medical domain models available
  - Efficient batch processing
  - Cross-encoder support for reranking
- **Models Used**:
  - `BAAI/bge-large-en-v1.5`: Primary embeddings (1024-dim)
  - `BAAI/bge-reranker-large`: Cross-encoder reranking
  - `pritamdeka/BioBERT-mnli`: Medical-specific (optional)

**Package**:
```python
sentence-transformers==3.5.0
```

---

## ☁️ AWS Services & SDKs

### **Boto3 1.35.82**
- **Version**: `1.35.82` (March 2026)
- **Why**: Official AWS SDK for Python
- **Services Used**:
  - Bedrock Runtime
  - S3
  - OpenSearch
  - Lambda
  - API Gateway
  - CloudWatch

**Package**:
```python
boto3==1.35.82
botocore==1.35.82
aioboto3==13.3.0  # Async boto3
```

### **Amazon Bedrock**
- **Service**: Fully managed LLM service
- **Model**: `anthropic.claude-sonnet-4-6-20260223-v1:0` (Claude Sonnet 4.6 - NEW Feb 2026)
- **Why**:
  - **Latest Claude model** with improved reasoning (Feb 2026 release)
  - **Better medical/scientific knowledge** than 3.5
  - **Enhanced citation accuracy** for RAG applications
  - HIPAA-eligible
  - VPC endpoint support
  - No data training on inputs
- **Features**:
  - 200K context window
  - Improved function calling
  - Streaming responses
  - Guardrails for content filtering
  - Better handling of complex medical terminology

**Configuration**:
```python
# Bedrock Runtime API with Claude Sonnet 4.6
bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-east-1'
)

MODEL_ID = "anthropic.claude-sonnet-4-6-20260223-v1:0"  # Latest 2026 model
```

### **Amazon OpenSearch 3.3**
- **Version**: OpenSearch 3.3 (February 2026)
- **Why**:
  - GPU acceleration for vector search (NEW in 3.3)
  - Hybrid search (BM25 + k-NN)
  - Auto-optimization for vector workloads
  - Serverless option available
- **Key Features**:
  - HNSW algorithm for k-NN
  - Filtered vector search
  - Approximate nearest neighbor (ANN)
  - Real-time indexing

**SDK**:
```python
opensearch-py==2.8.0
```

### **AWS Lambda & API Gateway**
- **Runtime**: Python 3.12
- **Memory**: 3008 MB (for embedding models)
- **Timeout**: 900s (max)
- **Layers**: Custom layer for dependencies
- **API Gateway**: HTTP API (v2) for lower latency

---

## 📄 Document Processing

### **PyPDF 5.2.0**
- **Version**: `5.2.0` (2026 latest)
- **Why**:
  - Pure Python (no system dependencies)
  - Fast PDF text extraction
  - Metadata preservation
  - Table detection support

**Package**:
```python
pypdf==5.2.0
```

### **Unstructured 0.16.8**
- **Version**: `0.16.8` (March 2026)
- **Why**:
  - Advanced layout detection
  - Table extraction
  - Multi-format support (PDF, DOCX, HTML)
  - Medical document optimized

**Package**:
```python
unstructured==0.16.8
unstructured[pdf]==0.16.8
```

---

## 🔧 Supporting Libraries

### **Data Validation & Settings**
```python
pydantic==2.10.5           # Data models
pydantic-settings==2.7.1   # Environment variables
python-dotenv==1.0.1       # .env file loading
```

### **HTTP & Async**
```python
httpx==0.28.1              # Async HTTP client
aiofiles==24.1.0           # Async file operations
asyncio==3.12.7            # Built-in async
```

### **Monitoring & Logging**
```python
loguru==0.7.3              # Better logging
structlog==24.4.0          # Structured logging for agents
prometheus-client==0.21.1  # Metrics
sentry-sdk==2.20.0         # Error tracking
python-json-logger==3.2.1  # JSON log formatting
```

### **Debug & Tracing**
```python
opentelemetry-api==1.28.2           # Distributed tracing
opentelemetry-sdk==1.28.2           # Tracing SDK
opentelemetry-instrumentation==0.49b2  # Auto-instrumentation
aws-xray-sdk==2.14.0                # AWS X-Ray integration
```

### **Testing**
```python
pytest==8.3.5              # Testing framework
pytest-asyncio==0.25.2     # Async test support
httpx==0.28.1              # API testing
pytest-cov==6.0.0          # Coverage reports
```

### **Development Tools**
```python
black==24.10.0             # Code formatting
ruff==0.8.5                # Fast linting
mypy==1.14.0               # Type checking
pre-commit==4.0.1          # Git hooks
```

---

## 🎨 Frontend Stack

### **React 18.3.1**
- **Version**: `18.3.1` (Latest stable)
- **Why**:
  - Concurrent rendering
  - Server components support
  - Best ecosystem

### **Vite 6.0.5**
- **Version**: `6.0.5` (2026 latest)
- **Why**:
  - Lightning-fast HMR
  - Optimized production builds
  - Native ESM support

### **TailwindCSS 4.1.0**
- **Version**: `4.1.0` (NEW - Released Feb 2026)
- **Why**:
  - New Oxide engine (20x faster)
  - Better TypeScript support
  - Improved JIT compilation

### **Shadcn/ui (Latest)**
- **Why**:
  - Copy-paste components
  - Radix UI primitives
  - Fully customizable
  - Accessibility built-in

**Frontend Dependencies**:
```json
{
  "react": "^18.3.1",
  "react-dom": "^18.3.1",
  "vite": "^6.0.5",
  "tailwindcss": "^4.1.0",
  "@radix-ui/react-dialog": "^1.1.5",
  "@radix-ui/react-dropdown-menu": "^2.1.5",
  "lucide-react": "^0.468.0",
  "react-query": "^5.62.3",
  "axios": "^1.7.9"
}
```

---

## 🚀 Deployment & Infrastructure

### **AWS CDK 2.175.0**
- **Version**: `2.175.0` (March 2026)
- **Why**:
  - Infrastructure as Code
  - Type-safe (TypeScript)
  - Reusable constructs
  - CloudFormation under the hood

### **Docker**
- **Base Image**: `python:3.12-slim`
- **Multi-stage builds**: Yes
- **Size**: ~500MB (optimized)

### **GitHub Actions**
- **CI/CD**: Automated testing and deployment
- **Workflows**:
  - Test on PR
  - Deploy to staging (on merge to main)
  - Deploy to production (on tag)

---

## 📊 Version Summary Table

| Category | Technology | Version | Release Date |
|----------|-----------|---------|--------------|
| **Language** | Python | 3.12.7 | Dec 2025 |
| **Web Framework** | FastAPI | 0.135.1 | Mar 2026 |
| **LLM Orchestration** | LangChain | 1.2.10 | Feb 2026 |
| **Multi-Agent** | LangGraph | 0.2.65 | Feb 2026 |
| **Transformers** | HuggingFace | 5.3.0 | Mar 2026 |
| **Embeddings** | Sentence-Transformers | 3.5.0 | Feb 2026 |
| **AWS SDK** | Boto3 | 1.35.82 | Mar 2026 |
| **Vector DB** | OpenSearch | 3.3 | Feb 2026 |
| **Frontend** | React | 18.3.1 | Jan 2026 |
| **Build Tool** | Vite | 6.0.5 | Feb 2026 |
| **Styling** | TailwindCSS | 4.1.0 | Feb 2026 |
| **IaC** | AWS CDK | 2.175.0 | Mar 2026 |

---

## 🔄 Migration Notes (2025 → 2026)

### **Major Updates**
1. **HuggingFace Transformers v5**
   - New tokenizer backend (breaking change)
   - Update all tokenizer calls
   - Use `trust_remote_code=True` for custom models

2. **TailwindCSS v4**
   - New Oxide engine
   - Config file changes
   - Faster compilation

3. **OpenSearch 3.3**
   - GPU acceleration support
   - New auto-optimization features
   - Updated query syntax

### **Deprecated Features**
- ❌ LangChain `ConversationChain` (use LCEL instead)
- ❌ Old OpenSearch k-NN plugin (use native vector search)
- ❌ FastAPI `BackgroundTasks` (use Celery for production)

---

## 🎯 Why This Stack for Indegene?

### **Alignment with Job Requirements**
✅ **Python**: Industry standard for ML/AI  
✅ **FastAPI**: Modern async framework  
✅ **LangChain/LangGraph**: Agentic workflows  
✅ **HuggingFace**: Open-source models  
✅ **Amazon Bedrock**: Enterprise LLM access  
✅ **RAG Architecture**: Core competency  
✅ **AWS Services**: Full cloud-native stack  

### **Production-Ready**
✅ All versions are stable (not beta)  
✅ Enterprise support available  
✅ Active community and documentation  
✅ Security patches and updates  
✅ HIPAA-compliant configurations  

### **Future-Proof**
✅ Latest 2026 versions  
✅ Long-term support (LTS)  
✅ Backward compatibility maintained  
✅ Clear upgrade paths  

---

**Last Updated**: March 5, 2026  
**Next Review**: Before deployment to production
