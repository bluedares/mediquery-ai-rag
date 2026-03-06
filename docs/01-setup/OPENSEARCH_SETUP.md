# OpenSearch Setup Guide

## Current Implementation Review

### Code Analysis
- **Location**: `backend/app/services/opensearch.py`
- **Mock Mode**: Enabled when `OPENSEARCH_ENDPOINT` is empty
- **Real Mode**: Requires OpenSearch endpoint URL

### Connection Details (from code)
```python
self.client = OpenSearch(
    hosts=[self.endpoint],
    http_auth=('admin', 'Admin123!'),  # Hardcoded credentials
    use_ssl=True,
    verify_certs=False,
    ssl_show_warn=False
)
```

## OPENSEARCH_ENDPOINT Format

The endpoint should be in this format:
```
https://your-domain-name.us-east-1.es.amazonaws.com
```

**Example:**
```
OPENSEARCH_ENDPOINT=https://mediquery-search.us-east-1.es.amazonaws.com
```

## Options to Get Real OpenSearch

### Option 1: AWS OpenSearch Service (Recommended)
**Pros:**
- Fully managed
- Integrated with AWS
- Automatic backups
- Scalable

**Cons:**
- Costs money (~$0.10-0.50/hour for t3.small)
- Takes 10-15 minutes to create

**Steps:**
1. Go to AWS Console → OpenSearch Service
2. Click "Create domain"
3. Choose:
   - Domain name: `mediquery-search`
   - Deployment type: Development/testing
   - Instance type: t3.small.search
   - Number of nodes: 1
   - Network: Public access (for testing)
   - Access policy: Allow specific IP or IAM
4. Wait 10-15 minutes for creation
5. Copy the endpoint URL
6. Update `.env`: `OPENSEARCH_ENDPOINT=https://...`

### Option 2: Local OpenSearch (Docker)
**Pros:**
- Free
- Fast setup
- Good for development

**Cons:**
- Runs on your machine
- Not persistent across restarts
- Not suitable for production

**Steps:**
```bash
# Run OpenSearch in Docker
docker run -d \
  --name opensearch-node \
  -p 9200:9200 \
  -p 9600:9600 \
  -e "discovery.type=single-node" \
  -e "OPENSEARCH_INITIAL_ADMIN_PASSWORD=Admin123!" \
  opensearchproject/opensearch:latest

# Update .env
OPENSEARCH_ENDPOINT=https://localhost:9200
```

### Option 3: OpenSearch Serverless (AWS)
**Pros:**
- Pay per use
- No infrastructure management
- Auto-scaling

**Cons:**
- Different API
- Requires code changes
- More expensive for small workloads

## Security Considerations

### Current Issues in Code:
1. **Hardcoded credentials**: `('admin', 'Admin123!')`
2. **Certificate verification disabled**: `verify_certs=False`
3. **No secrets management**

### Recommended Fixes:
1. Use AWS Secrets Manager for credentials
2. Enable certificate verification in production
3. Use IAM authentication for AWS OpenSearch

## Cost Estimate (AWS OpenSearch Service)

**Development Setup:**
- Instance: t3.small.search
- Storage: 10GB
- **Cost**: ~$0.10/hour = ~$72/month

**Can be stopped when not in use to save costs**

## Next Steps

1. **Choose an option** (AWS OpenSearch Service recommended)
2. **Create the OpenSearch domain/instance**
3. **Get the endpoint URL**
4. **Update `.env`**:
   ```
   OPENSEARCH_ENDPOINT=https://your-endpoint-here
   ```
5. **Restart backend**
6. **Test**: Embeddings will be stored in real OpenSearch instead of mock

## Why Remove Mock Mode?

**Current Mock Mode:**
- Stores embeddings in memory
- Lost on restart
- Not suitable for production
- Limited search capabilities

**Real OpenSearch:**
- Persistent storage
- Advanced vector search
- Better performance
- Production-ready
