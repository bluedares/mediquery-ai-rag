# Requirements Analysis - MediQuery AI

## 📋 Project Requirements

This document analyzes the requirements for building a healthcare LLM application that demonstrates Indegene's tech stack.

---

## 🎯 Business Requirements

### Primary Objective
Build a **production-grade demo** that showcases:
1. Multi-agent LLM orchestration
2. RAG (Retrieval-Augmented Generation) architecture
3. Healthcare-specific use case
4. Complete AWS deployment
5. HIPAA-compliant design

### Success Criteria
- ✅ Demonstrates ALL required tech stack components
- ✅ Solves a real healthcare problem
- ✅ Production-ready code quality
- ✅ Deployable to AWS
- ✅ Interview-ready presentation

---

## 🔧 Technical Requirements

### Must-Have Technologies (From Job Description)

| Technology | Version | Usage | Status |
|-----------|---------|-------|--------|
| **Python** | 3.12.7 | Backend language | ✅ |
| **FastAPI** | 0.135.1 | Web framework | ✅ |
| **LangChain** | 1.2.10 | LLM orchestration | ✅ |
| **LangGraph** | 0.2.65 | Multi-agent workflows | ✅ |
| **HuggingFace Transformers** | 5.3.0 | Embeddings | ✅ |
| **Amazon Bedrock** | Latest | LLM inference | ✅ |
| **RAG Architecture** | Custom | Document Q&A | ✅ |
| **Vector Search** | OpenSearch 3.3 | Semantic search | ✅ |
| **AWS EKS** | Latest | Container orchestration | 🔶 Optional |
| **AWS Lambda** | Python 3.12 | Serverless compute | ✅ |
| **AWS API Gateway** | HTTP API v2 | API management | ✅ |
| **AWS S3** | Latest | Document storage | ✅ |
| **AWS OpenSearch** | 3.3 | Vector database | ✅ |

**Legend**: ✅ Required | 🔶 Optional/Nice-to-have

---

## 🏥 Functional Requirements

### FR1: Document Upload & Processing
**Priority**: High

**Description**: Users can upload medical PDFs for processing

**Acceptance Criteria**:
- [ ] Support PDF files up to 50MB
- [ ] Extract text with layout preservation
- [ ] Handle tables and structured data
- [ ] Generate metadata (title, authors, sections)
- [ ] Process within 30 seconds for 50-page document
- [ ] Store original PDF in S3
- [ ] Create searchable chunks (512 tokens each)

**Technical Implementation**:
```python
POST /api/v1/upload
Content-Type: multipart/form-data

Request:
{
  "file": <binary>,
  "metadata": {
    "document_type": "clinical_trial",
    "tags": ["phase_3", "oncology"]
  }
}

Response:
{
  "document_id": "doc_123",
  "status": "processing",
  "chunks_created": 47,
  "processing_time": 23.4
}
```

---

### FR2: Intelligent Question Answering
**Priority**: High

**Description**: Users can ask natural language questions about uploaded documents

**Acceptance Criteria**:
- [ ] Support natural language queries
- [ ] Return answers with source citations
- [ ] Provide confidence scores
- [ ] Handle follow-up questions
- [ ] Response time < 3 seconds (p95)
- [ ] Support multiple query types (factual, analytical, comparative)

**Technical Implementation**:
```python
POST /api/v1/query
Content-Type: application/json

Request:
{
  "query": "What are the primary endpoints of this trial?",
  "document_id": "doc_123",
  "conversation_id": "conv_456"  # Optional for follow-ups
}

Response:
{
  "answer": "The primary endpoints are:\n1. Overall Survival (OS)...",
  "citations": [
    {
      "document_id": "doc_123",
      "page": 12,
      "section": "Study Design",
      "text": "Primary endpoint: OS at 24 months",
      "relevance_score": 0.92
    }
  ],
  "confidence": 0.89,
  "processing_time": 2.3,
  "agent_trace": {
    "query_analyzer": {"intent": "factual_lookup"},
    "retrieval": {"chunks_retrieved": 20},
    "reranking": {"chunks_selected": 5},
    "synthesis": {"tokens_used": 1234}
  }
}
```

---

### FR3: Multi-Agent Workflow Visibility
**Priority**: Medium

**Description**: Show how different agents collaborate to answer queries

**Acceptance Criteria**:
- [ ] Display agent execution flow
- [ ] Show intermediate results from each agent
- [ ] Provide timing information per agent
- [ ] Enable debugging of agent decisions

**Technical Implementation**:
```python
GET /api/v1/query/{query_id}/trace

Response:
{
  "query_id": "q_789",
  "workflow": [
    {
      "agent": "QueryAnalyzerAgent",
      "input": "What are the side effects?",
      "output": {
        "intent": "safety_lookup",
        "strategy": "hybrid_search"
      },
      "duration_ms": 150
    },
    {
      "agent": "RetrievalAgent",
      "input": {"query": "...", "strategy": "hybrid"},
      "output": {"chunks": 20, "avg_score": 0.78},
      "duration_ms": 450
    },
    ...
  ]
}
```

---

### FR4: Document Management
**Priority**: Medium

**Description**: Users can list, view, and delete uploaded documents

**Acceptance Criteria**:
- [ ] List all uploaded documents
- [ ] View document metadata
- [ ] Delete documents (with cascade to chunks)
- [ ] Search documents by metadata
- [ ] Pagination support

**Technical Implementation**:
```python
GET /api/v1/documents?page=1&limit=20&type=clinical_trial

Response:
{
  "documents": [
    {
      "document_id": "doc_123",
      "filename": "trial_protocol.pdf",
      "upload_date": "2026-03-05T10:30:00Z",
      "size_bytes": 2048576,
      "chunks": 47,
      "status": "indexed",
      "metadata": {...}
    }
  ],
  "total": 156,
  "page": 1,
  "pages": 8
}
```

---

## 🔒 Non-Functional Requirements

### NFR1: Security & Privacy
**Priority**: Critical

**Requirements**:
- [ ] All data encrypted at rest (AES-256)
- [ ] All data encrypted in transit (TLS 1.3)
- [ ] VPC-isolated architecture
- [ ] No data sent to third-party model providers
- [ ] HIPAA-eligible AWS services only
- [ ] Audit logging for all API calls
- [ ] API authentication (Cognito or API keys)
- [ ] Rate limiting (100 req/min per user)

**Compliance**:
- HIPAA Technical Safeguards
- GDPR data protection
- SOC 2 Type II controls

---

### NFR2: Performance
**Priority**: High

**Requirements**:

| Metric | Target | Measurement |
|--------|--------|-------------|
| Query Response Time (p50) | < 1.5s | CloudWatch |
| Query Response Time (p95) | < 3.0s | CloudWatch |
| Query Response Time (p99) | < 5.0s | CloudWatch |
| Document Processing | < 30s per 50 pages | Application logs |
| API Availability | 99.9% | CloudWatch |
| Concurrent Users | 100+ | Load testing |
| Throughput | 50 queries/sec | Load testing |

**Performance Testing**:
```bash
# Load test with k6
k6 run --vus 100 --duration 5m load-test.js
```

---

### NFR3: Scalability
**Priority**: High

**Requirements**:
- [ ] Auto-scaling Lambda (up to 1000 concurrent)
- [ ] OpenSearch cluster scales with data volume
- [ ] S3 unlimited storage
- [ ] Stateless API design
- [ ] Horizontal scaling support
- [ ] Handle 10,000+ documents
- [ ] Support 10M+ vector embeddings

**Scaling Triggers**:
```yaml
Lambda:
  - Metric: ConcurrentExecutions
  - Threshold: > 80% of reserved concurrency
  - Action: Request limit increase

OpenSearch:
  - Metric: CPUUtilization
  - Threshold: > 70% for 10 minutes
  - Action: Add data node
```

---

### NFR4: Reliability
**Priority**: High

**Requirements**:
- [ ] Automated error recovery
- [ ] Retry logic with exponential backoff
- [ ] Circuit breakers for external services
- [ ] Health checks for all components
- [ ] Graceful degradation
- [ ] Data backup and recovery
- [ ] Multi-AZ deployment

**Error Handling**:
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def call_bedrock(prompt: str):
    """Call Bedrock with retry logic"""
    try:
        return await bedrock_client.invoke_model(...)
    except ClientError as e:
        if e.response['Error']['Code'] == 'ThrottlingException':
            raise  # Retry
        else:
            logger.error(f"Bedrock error: {e}")
            return fallback_response()
```

---

### NFR5: Observability
**Priority**: High

**Requirements**:
- [ ] Structured logging (JSON format)
- [ ] Distributed tracing (X-Ray)
- [ ] Custom metrics (CloudWatch)
- [ ] Error tracking (Sentry)
- [ ] Performance monitoring
- [ ] Cost tracking
- [ ] Alerting on anomalies

**Logging Standard**:
```python
import structlog

logger = structlog.get_logger()

logger.info(
    "query_processed",
    request_id=request_id,
    user_id=user_id,
    query=query,
    latency_ms=latency,
    chunks_retrieved=len(chunks),
    bedrock_tokens=tokens,
    cost_usd=cost
)
```

---

### NFR6: Maintainability
**Priority**: Medium

**Requirements**:
- [ ] Clean code architecture
- [ ] Comprehensive documentation
- [ ] Unit test coverage > 80%
- [ ] Integration tests for critical paths
- [ ] Type hints throughout
- [ ] Linting (Ruff) and formatting (Black)
- [ ] Pre-commit hooks
- [ ] CI/CD pipeline

**Code Quality Checks**:
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    hooks:
      - id: ruff
        args: [--fix]
  
  - repo: https://github.com/psf/black
    hooks:
      - id: black
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    hooks:
      - id: mypy
```

---

## 📊 Data Requirements

### Document Types Supported
1. **Clinical Trial Protocols**
   - Format: PDF
   - Size: Up to 200 pages
   - Structure: Sections, tables, references

2. **Drug Labels**
   - Format: PDF
   - Size: 10-50 pages
   - Structure: Standardized sections (indications, dosage, warnings)

3. **Patient Information Leaflets**
   - Format: PDF
   - Size: 5-20 pages
   - Structure: Q&A format, simple language

### Data Volume Estimates
```yaml
Initial_Load:
  Documents: 100
  Total_Pages: 5000
  Total_Chunks: 25000
  Vector_Dimensions: 1024
  Storage_Required: 5GB

Year_1_Growth:
  Documents: 1000
  Total_Pages: 50000
  Total_Chunks: 250000
  Storage_Required: 50GB

Queries_Per_Day: 1000
Avg_Query_Length: 50 tokens
Avg_Response_Length: 200 tokens
```

---

## 🎨 User Interface Requirements

### UI Components
1. **Document Upload Page**
   - Drag-and-drop file upload
   - Upload progress indicator
   - Document metadata form
   - Processing status

2. **Query Interface**
   - Chat-style interface
   - Query input with autocomplete
   - Response with citations
   - Source highlighting
   - Agent workflow visualization

3. **Document Library**
   - Grid/list view toggle
   - Search and filter
   - Document preview
   - Delete confirmation

4. **Admin Dashboard** (Optional)
   - System health metrics
   - Usage statistics
   - Cost tracking
   - User management

### Accessibility Requirements
- WCAG 2.1 AA compliance
- Keyboard navigation
- Screen reader support
- High contrast mode
- Responsive design (mobile-friendly)

---

## 🚀 Deployment Requirements

### Infrastructure as Code
- [ ] AWS CDK or Terraform
- [ ] Separate environments (dev, staging, prod)
- [ ] Automated deployment pipeline
- [ ] Rollback capability
- [ ] Blue-green deployment support

### CI/CD Pipeline
```yaml
Stages:
  1. Code_Quality:
     - Linting (Ruff)
     - Type checking (mypy)
     - Security scan (Bandit)
  
  2. Testing:
     - Unit tests (pytest)
     - Integration tests
     - Coverage report (>80%)
  
  3. Build:
     - Docker image build
     - Lambda layer creation
     - Frontend build (Vite)
  
  4. Deploy_Staging:
     - Deploy to staging
     - Run smoke tests
     - Performance tests
  
  5. Deploy_Production:
     - Manual approval
     - Blue-green deployment
     - Health checks
     - Rollback on failure
```

---

## 📅 Timeline & Milestones

### Phase 1: Foundation (Day 1)
- [x] Requirements analysis
- [x] Architecture design
- [x] Tech stack finalization
- [ ] Project setup
- [ ] Development environment

### Phase 2: Core Development (Days 2-3)
- [ ] FastAPI backend structure
- [ ] LangGraph multi-agent system
- [ ] Document processing pipeline
- [ ] RAG implementation
- [ ] OpenSearch integration
- [ ] Bedrock integration

### Phase 3: Frontend & Integration (Day 4)
- [ ] React frontend
- [ ] API integration
- [ ] End-to-end testing
- [ ] Bug fixes

### Phase 4: AWS Deployment (Day 5)
- [ ] Infrastructure setup
- [ ] Lambda deployment
- [ ] OpenSearch configuration
- [ ] API Gateway setup
- [ ] Monitoring & logging

### Phase 5: Demo Preparation (Day 6)
- [ ] Sample data preparation
- [ ] Demo script
- [ ] Documentation
- [ ] Interview talking points

---

## ✅ Acceptance Criteria

### Minimum Viable Product (MVP)
- ✅ Upload PDF documents
- ✅ Ask questions and get cited answers
- ✅ Multi-agent workflow visible
- ✅ Deployed to AWS
- ✅ Basic monitoring

### Interview-Ready Demo
- ✅ All tech stack components demonstrated
- ✅ Production-quality code
- ✅ Comprehensive documentation
- ✅ Working AWS deployment
- ✅ Performance metrics available
- ✅ Security best practices implemented

### Bonus Features (If Time Permits)
- 🔶 Conversation memory
- 🔶 Document comparison
- 🔶 Entity extraction
- 🔶 Admin dashboard
- 🔶 Multi-region deployment

---

## 🎯 Out of Scope

**Explicitly NOT included**:
- ❌ User authentication system (use API keys for demo)
- ❌ Payment processing
- ❌ Mobile apps
- ❌ Real-time collaboration
- ❌ OCR for scanned documents
- ❌ Multi-language support
- ❌ Custom model training

---

## 📝 Assumptions

1. **AWS Account**: You have access to an AWS account with appropriate permissions
2. **Bedrock Access**: Claude 3.5 Sonnet is available in your region
3. **Sample Data**: We'll use publicly available clinical trial documents
4. **Demo Environment**: Deployment is for demo purposes, not production traffic
5. **Time Constraint**: 6 days to build and deploy
6. **Budget**: AWS costs < $100 for demo period

---

## 🔄 Change Management

**Requirement Changes**:
- All requirement changes must be documented
- Impact analysis required for major changes
- Update timeline and milestones accordingly

**Version Control**:
- Requirements document version: 1.0
- Last updated: March 5, 2026
- Next review: Before Phase 2 starts

---

**Requirements Status**: ✅ Finalized  
**Approved By**: Development Team  
**Date**: March 5, 2026
