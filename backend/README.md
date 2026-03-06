# MediQuery AI - Backend

Production-grade FastAPI backend with multi-agent RAG system.

## 🚀 Quick Start

### Prerequisites
- Python 3.12.7+
- AWS Account with Bedrock access
- Virtual environment

### Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your AWS credentials
nano .env
```

### Run Development Server

```bash
# Start FastAPI server
uvicorn app.main:app --reload --port 8000

# Or use the main.py directly
python -m app.main
```

### Access API

- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📁 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Settings & debug config
│   ├── models/              # Pydantic models
│   │   ├── requests.py
│   │   └── responses.py
│   ├── api/                 # API routes
│   │   ├── upload.py
│   │   ├── query.py
│   │   └── documents.py
│   ├── agents/              # LangGraph agents
│   │   ├── graph.py
│   │   ├── query_analyzer.py
│   │   ├── retrieval.py
│   │   ├── reranking.py
│   │   └── synthesis.py
│   ├── services/            # External services
│   │   ├── bedrock.py
│   │   ├── opensearch.py
│   │   ├── s3.py
│   │   └── embeddings.py
│   └── utils/               # Utilities
│       ├── logger.py
│       ├── tracing.py
│       └── llm_tracer.py
├── tests/                   # Test suite
├── logs/                    # Log files
├── requirements.txt
├── .env.example
└── README.md
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_debug_system.py -v

# Run Phase 0 validation
python test_phase0.py
```

## 🔧 Configuration

### Environment Variables

```bash
# AWS
AWS_REGION=us-east-1
S3_BUCKET=mediquery-documents
OPENSEARCH_ENDPOINT=
BEDROCK_MODEL_ID=anthropic.claude-sonnet-4-6-20260223-v1:0

# Debug
DEBUG_MODE=true
LOG_LEVEL=DEBUG
TRACE_AGENTS=true
TRACE_LLM_CALLS=true
```

### Debug Flags

- `DEBUG_MODE`: Enable debug features
- `TRACE_AGENTS`: Log agent execution
- `TRACE_LLM_CALLS`: Log LLM API calls
- `TRACE_LLM_PROMPTS`: Log prompts
- `TRACE_LLM_RESPONSES`: Log responses

## 📊 API Endpoints

### Health Check
```bash
GET /health
```

### Upload Document
```bash
POST /api/v1/upload
Content-Type: multipart/form-data

{
  "file": <binary>,
  "document_type": "clinical_trial",
  "tags": ["phase_3", "oncology"]
}
```

### Query Document
```bash
POST /api/v1/query
Content-Type: application/json

{
  "query": "What are the primary endpoints?",
  "document_id": "doc_123",
  "include_trace": true
}
```

### List Documents
```bash
GET /api/v1/documents?page=1&limit=20
```

## 🐛 Debugging

### View Logs

```bash
# Console logs (real-time)
tail -f logs/mediquery.log

# Structured logs
cat logs/mediquery.log | jq
```

### Debug Mode

```python
# Enable all tracing
DEBUG_MODE=true
TRACE_AGENTS=true
TRACE_LLM_CALLS=true
TRACE_LLM_PROMPTS=true
TRACE_LLM_RESPONSES=true
```

### Agent Trace Example

```json
{
  "agent_trace": [
    {
      "agent": "QueryAnalyzerAgent",
      "duration_ms": 45.2,
      "status": "success"
    },
    {
      "agent": "RetrievalAgent",
      "duration_ms": 234.5,
      "status": "success"
    }
  ]
}
```

## 🚀 Deployment

### Docker

```bash
# Build image
docker build -t mediquery-backend .

# Run container
docker run -p 8000:8000 --env-file .env mediquery-backend
```

### AWS Lambda

```bash
# Package for Lambda
pip install -r requirements.txt -t package/
cd package && zip -r ../lambda.zip .
cd .. && zip -g lambda.zip app/**/*.py

# Deploy with AWS CLI
aws lambda update-function-code \
  --function-name mediquery-api \
  --zip-file fileb://lambda.zip
```

## 📈 Performance

- **Response Time (p95)**: < 3s
- **Concurrent Requests**: 100+
- **Throughput**: 50 queries/sec

## 🔐 Security

- VPC-isolated deployment
- KMS encryption at rest
- TLS 1.3 in transit
- HIPAA-compliant configuration

## 📝 License

Built for Indegene Interview - March 2026
