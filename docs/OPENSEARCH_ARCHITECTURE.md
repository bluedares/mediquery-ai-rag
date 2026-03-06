# OpenSearch Architecture Documentation

## Overview

OpenSearch is a distributed search and analytics engine used for vector similarity search in our RAG (Retrieval-Augmented Generation) system.

## Why OpenSearch Domain is Required

### OpenSearch is a Service, Not Just Storage

**Key Concept**: OpenSearch is a **running server/service**, not just a storage location.

```
❌ Cannot do: AWS Access Keys → OpenSearch (No server to connect to)
✅ Must do: AWS Access Keys → OpenSearch Domain (Running server) → Vector Database
```

**Analogy**:
- **S3**: Like a file cabinet - just store and retrieve files with access keys
- **OpenSearch**: Like a MySQL server - needs running instance with endpoint URL

### What is an OpenSearch Domain?

An OpenSearch Domain is:
- A managed cluster of OpenSearch nodes
- Running 24/7 on AWS infrastructure
- Has its own endpoint URL (e.g., `https://mediquery-search-xxxxx.us-east-1.es.amazonaws.com`)
- Processes complex vector similarity searches
- Manages indexes, shards, and replicas

## Architecture Flow

```
┌─────────────┐
│   User      │
│  Uploads    │
│    PDF      │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│              Backend Processing                         │
│                                                          │
│  1. Extract text from PDF                               │
│  2. Split into chunks (512 tokens)                      │
│  3. Generate embeddings (1024-dim vectors)              │
│     using BAAI/bge-large-en-v1.5                       │
└──────┬──────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│              Storage Layer                              │
│                                                          │
│  ┌──────────────┐         ┌─────────────────────────┐  │
│  │     S3       │         │   OpenSearch Domain     │  │
│  │              │         │                         │  │
│  │ Store PDFs   │         │ Store:                  │  │
│  │ (Original)   │         │ - Vector embeddings     │  │
│  │              │         │ - Document metadata     │  │
│  │              │         │ - Full text chunks      │  │
│  └──────────────┘         │ - Enable k-NN search    │  │
│                           └─────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│              Query Processing                           │
│                                                          │
│  1. User asks question                                  │
│  2. Convert question to embedding                       │
│  3. OpenSearch k-NN search (find similar vectors)       │
│  4. Retrieve top-k relevant chunks                      │
│  5. Send to Bedrock Claude                              │
│  6. Generate answer                                     │
└─────────────────────────────────────────────────────────┘
```

## Why Not Just Use S3?

| Feature | S3 | OpenSearch Domain |
|---------|----|--------------------|
| Store files | ✅ | ❌ |
| Vector similarity search | ❌ | ✅ |
| k-NN search (cosine similarity) | ❌ | ✅ |
| Hybrid search (semantic + keyword) | ❌ | ✅ |
| Real-time indexing | ❌ | ✅ |
| Sub-second query performance | ❌ | ✅ |
| Filtering by metadata | ❌ | ✅ |

**We use both:**
- **S3**: Store original PDFs (immutable, cheap storage)
- **OpenSearch**: Store embeddings + enable fast vector search

## Authentication Methods

### Option 1: Master Username/Password (Current Implementation)

**Pros:**
- Simple to set up
- Works immediately
- Good for development

**Cons:**
- Credentials in code/env file
- Less secure
- Manual credential rotation

**Implementation:**
```python
from opensearchpy import OpenSearch

client = OpenSearch(
    hosts=['https://your-domain.us-east-1.es.amazonaws.com'],
    http_auth=('admin', 'Admin123!'),  # Master user credentials
    use_ssl=True,
    verify_certs=True
)
```

**Configuration:**
```bash
# .env file
OPENSEARCH_ENDPOINT=https://mediquery-search-xxxxx.us-east-1.es.amazonaws.com
OPENSEARCH_USERNAME=admin
OPENSEARCH_PASSWORD=Admin123!
```

### Option 2: AWS IAM Authentication (Recommended for Production)

**Pros:**
- Uses existing AWS credentials
- More secure (no passwords in code)
- Automatic credential rotation
- Fine-grained access control

**Cons:**
- Slightly more complex setup
- Requires additional library

**Implementation:**
```python
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3

# Get AWS credentials
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(
    credentials.access_key,
    credentials.secret_key,
    'us-east-1',
    'es',
    session_token=credentials.token
)

client = OpenSearch(
    hosts=['https://your-domain.us-east-1.es.amazonaws.com'],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)
```

**Configuration:**
```bash
# .env file
OPENSEARCH_ENDPOINT=https://mediquery-search-xxxxx.us-east-1.es.amazonaws.com
OPENSEARCH_AUTH_TYPE=iam  # Use IAM instead of basic auth
AWS_ACCESS_KEY_ID=AKIAXXXXX
AWS_SECRET_ACCESS_KEY=xxxxx
AWS_REGION=us-east-1
```

## Mock Mode vs Real OpenSearch

### Mock Mode (Current - Development Only)

**How it works:**
```python
# In-memory storage
self.mock_data = {
    "doc_123_chunk_1": {
        "embedding": [0.1, 0.2, ..., 0.9],  # 1024 dimensions
        "text": "Patient has diabetes...",
        "metadata": {"document_id": "doc_123", "page": 1}
    }
}
```

**Limitations:**
- ❌ Lost on restart
- ❌ No persistence
- ❌ Limited search capabilities
- ❌ Not scalable
- ❌ Not production-ready

### Real OpenSearch (Production)

**How it works:**
```python
# Persistent storage in OpenSearch cluster
client.index(
    index="medical-documents",
    id="doc_123_chunk_1",
    body={
        "embedding": [0.1, 0.2, ..., 0.9],
        "text": "Patient has diabetes...",
        "metadata": {"document_id": "doc_123", "page": 1}
    }
)
```

**Benefits:**
- ✅ Persistent across restarts
- ✅ Fast vector similarity search
- ✅ Scalable to millions of documents
- ✅ Advanced filtering and aggregations
- ✅ Production-ready

## Data Flow Example

### 1. Document Upload
```python
# User uploads: medical_report.pdf (15 pages)

# Backend processes:
chunks = extract_and_chunk(pdf)  # 45 chunks (512 tokens each)

for chunk in chunks:
    embedding = model.encode(chunk.text)  # [1024 dimensions]
    
    opensearch.index(
        index="medical-documents",
        id=f"{document_id}_{chunk_id}",
        body={
            "embedding": embedding.tolist(),
            "text": chunk.text,
            "metadata": {
                "document_id": "doc_abc123",
                "page": chunk.page,
                "chunk_id": chunk.id,
                "title": "medical_report.pdf"
            }
        }
    )
```

### 2. Query Processing
```python
# User asks: "What is the patient's blood glucose level?"

# Backend processes:
query_embedding = model.encode(question)  # [1024 dimensions]

# OpenSearch k-NN search
results = opensearch.search(
    index="medical-documents",
    body={
        "size": 20,
        "query": {
            "knn": {
                "embedding": {
                    "vector": query_embedding.tolist(),
                    "k": 20
                }
            }
        },
        "filter": {
            "term": {"metadata.document_id": "doc_abc123"}
        }
    }
)

# Results: Top 20 most similar chunks
# [
#   {"score": 0.95, "text": "Blood glucose: 120 mg/dL", "page": 3},
#   {"score": 0.89, "text": "Fasting glucose levels...", "page": 5},
#   ...
# ]

# Send to Bedrock Claude for answer generation
answer = bedrock.invoke(
    prompt=f"Based on: {results}, answer: {question}"
)
```

## OpenSearch Domain Configuration

### Development Setup (What we created)

```yaml
Domain Name: mediquery-search
Version: OpenSearch 3.5
Deployment Type: Development and testing
Instance Type: r7g.medium.search
Number of Nodes: 1
Availability Zones: 1
Storage: 10 GB EBS (gp3)
Network: VPC access
Authentication: Fine-grained access control (master user)
Encryption: HTTPS for all traffic
Cost: ~$0.15/hour = ~$108/month
```

### Production Recommendations

```yaml
Deployment Type: Production
Instance Type: r6g.large.search or better
Number of Nodes: 3 (for high availability)
Availability Zones: 3
Storage: 100+ GB EBS (gp3)
Network: VPC access with private subnets
Authentication: IAM-based
Encryption: Node-to-node encryption enabled
Backups: Automated snapshots enabled
Monitoring: CloudWatch alarms configured
Cost: ~$1.50/hour = ~$1,080/month
```

## Security Best Practices

### Current Implementation (Development)
```python
# ⚠️ Hardcoded credentials
http_auth=('admin', 'Admin123!')
verify_certs=False  # Certificate verification disabled
```

### Production Recommendations

1. **Use AWS Secrets Manager**
```python
import boto3
import json

def get_opensearch_credentials():
    client = boto3.client('secretsmanager', region_name='us-east-1')
    secret = client.get_secret_value(SecretId='opensearch/credentials')
    return json.loads(secret['SecretString'])

creds = get_opensearch_credentials()
http_auth=(creds['username'], creds['password'])
```

2. **Enable Certificate Verification**
```python
verify_certs=True
ssl_show_warn=False
```

3. **Use IAM Authentication**
```python
# No passwords in code
http_auth=awsauth  # AWS4Auth object
```

4. **Network Security**
- Deploy in private VPC subnets
- Use security groups to restrict access
- Enable VPC endpoints for AWS services

## Monitoring and Maintenance

### Key Metrics to Monitor

1. **Cluster Health**
   - Status: Green (all shards allocated)
   - Node count
   - CPU utilization
   - Memory usage

2. **Search Performance**
   - Query latency (p50, p95, p99)
   - Indexing rate
   - Search rate

3. **Storage**
   - Disk usage
   - Shard size
   - Index size

### Maintenance Tasks

1. **Regular**
   - Monitor cluster health
   - Review slow query logs
   - Check disk space

2. **Periodic**
   - Rotate indices (if using time-based indices)
   - Update OpenSearch version
   - Review and optimize mappings

3. **As Needed**
   - Scale nodes up/down
   - Reindex with new mappings
   - Restore from snapshots

## Cost Optimization

### Development
- Use single node (1 AZ)
- Use smaller instance types (r7g.medium)
- Delete domain when not in use
- Use gp3 storage (cheaper than io1)

### Production
- Use reserved instances (save 30-50%)
- Right-size instance types based on usage
- Use data tiering (hot/warm/cold)
- Enable compression
- Set up automated snapshots to S3

## Troubleshooting

### Common Issues

1. **Connection Timeout**
   - Check security group rules
   - Verify VPC/subnet configuration
   - Ensure endpoint URL is correct

2. **Authentication Failed**
   - Verify username/password
   - Check IAM permissions
   - Ensure fine-grained access control is configured

3. **Slow Queries**
   - Check cluster health
   - Review shard allocation
   - Optimize index mappings
   - Consider scaling up

4. **Out of Memory**
   - Reduce batch size for indexing
   - Scale up instance type
   - Enable circuit breakers

## Next Steps

1. ✅ Create OpenSearch domain (In progress)
2. ⏳ Get domain endpoint URL
3. ⏳ Update `.env` with endpoint and credentials
4. ⏳ Test connection from backend
5. ⏳ Verify embeddings are stored correctly
6. ⏳ Test query flow end-to-end
7. 🔜 Upgrade to IAM authentication (production)
8. 🔜 Set up monitoring and alerts
9. 🔜 Configure automated backups

## References

- [AWS OpenSearch Service Documentation](https://docs.aws.amazon.com/opensearch-service/)
- [OpenSearch Python Client](https://opensearch.org/docs/latest/clients/python/)
- [Vector Search in OpenSearch](https://opensearch.org/docs/latest/search-plugins/knn/)
- [Fine-grained Access Control](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/fgac.html)
