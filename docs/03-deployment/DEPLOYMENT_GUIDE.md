# MediQuery AI - Deployment Guide

## 🚀 Deployment Options

Three deployment modes available:
1. **Local Development** - For testing and demos
2. **AWS Lambda** - Serverless production deployment
3. **Docker** - Containerized deployment

---

## 💻 Option 1: Local Development

**Perfect for**: Interview demos, development, testing

```bash
# Quick start
./deploy.sh local

# Or manually:
# Terminal 1 - Backend
cd backend
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

**Access:**
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## ☁️ Option 2: AWS Lambda (Serverless)

**Perfect for**: Production, auto-scaling, cost-effective

### **Prerequisites**

1. **AWS Account** with credentials configured
2. **AWS SAM CLI** installed
3. **Docker** installed (for building)

### **Install SAM CLI**

```bash
# macOS
brew tap aws/tap
brew install aws-sam-cli

# Verify
sam --version
```

### **Deploy to AWS**

```bash
# One-command deployment
./deploy.sh lambda

# Or step-by-step:
cd backend

# Build
sam build

# Deploy (first time - guided)
sam deploy --guided

# Deploy (subsequent times)
sam deploy
```

### **Configuration Prompts**

```
Stack Name: mediquery-stack
AWS Region: us-east-1
Confirm changes: Y
Allow SAM CLI IAM role creation: Y
Save arguments to config: Y
```

### **What Gets Created**

- ✅ Lambda function (mediquery-api)
- ✅ API Gateway (REST API)
- ✅ S3 bucket (document storage)
- ✅ OpenSearch domain (vector search)
- ✅ CloudWatch logs
- ✅ IAM roles and policies

### **After Deployment**

```bash
# Get API URL
aws cloudformation describe-stacks \
  --stack-name mediquery-stack \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text

# Test endpoint
curl https://your-api-id.execute-api.us-east-1.amazonaws.com/Prod/health
```

### **Update Frontend**

Update `frontend/src/App.jsx`:
```javascript
const API_URL = 'https://your-api-id.execute-api.us-east-1.amazonaws.com/Prod'
```

---

## 🐳 Option 3: Docker Deployment

**Perfect for**: Consistent environments, ECS/EKS deployment

### **Build Docker Image**

```bash
./deploy.sh docker

# Or manually:
cd backend
docker build -f Dockerfile.lambda -t mediquery-api:latest .
```

### **Run Locally**

```bash
docker run -p 8000:8080 \
  -e AWS_ACCESS_KEY_ID=your-key \
  -e AWS_SECRET_ACCESS_KEY=your-secret \
  mediquery-api:latest
```

### **Push to ECR**

```bash
# Create repository
aws ecr create-repository --repository-name mediquery-api

# Login
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Tag
docker tag mediquery-api:latest \
  <account-id>.dkr.ecr.us-east-1.amazonaws.com/mediquery-api:latest

# Push
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/mediquery-api:latest
```

---

## 📊 Cost Estimates

### **AWS Lambda (Serverless)**

**Free Tier:**
- 1M requests/month free
- 400,000 GB-seconds compute free

**After Free Tier:**
- $0.20 per 1M requests
- $0.0000166667 per GB-second

**Example:**
- 10,000 requests/month
- 2GB memory, 3s average duration
- **Cost**: ~$1-2/month

### **OpenSearch**

- t3.small.search: ~$30/month
- **For demo**: Use mock mode (free)

### **S3**

- First 50TB: $0.023 per GB
- **For demo**: <1GB = ~$0.02/month

### **Total Estimated Cost**

- **Development/Demo**: $0-5/month (using mock mode)
- **Production**: $30-50/month (with OpenSearch)

---

## 🔧 Environment Variables

### **Required for Production**

```bash
# AWS Credentials (auto-configured in Lambda)
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=wJalrXUtn...
AWS_REGION=us-east-1

# Services (auto-configured by SAM template)
S3_BUCKET_NAME=mediquery-documents-123456789
OPENSEARCH_ENDPOINT=search-mediquery-xxx.us-east-1.es.amazonaws.com
```

### **Optional**

```bash
# Debug Settings
DEBUG_MODE=true
TRACE_AGENTS=true
TRACE_LLM_CALLS=true
LOG_LEVEL=INFO

# Bedrock Model
BEDROCK_MODEL_ID=anthropic.claude-sonnet-4-6-20260223-v1:0
```

---

## 🧪 Testing Deployment

### **Health Check**

```bash
# Local
curl http://localhost:8000/health

# Lambda
curl https://your-api.execute-api.us-east-1.amazonaws.com/Prod/health
```

### **Query Test**

```bash
curl -X POST https://your-api.execute-api.us-east-1.amazonaws.com/Prod/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the primary endpoints?",
    "document_id": "doc_sample_001",
    "include_trace": true
  }'
```

---

## 📝 Deployment Checklist

### **Before Deploying**

- [ ] AWS credentials configured
- [ ] Bedrock model access enabled
- [ ] SAM CLI installed
- [ ] Docker installed (for Lambda)
- [ ] Environment variables set
- [ ] Code tested locally

### **After Deploying**

- [ ] API Gateway URL obtained
- [ ] Health check passes
- [ ] Test query successful
- [ ] Frontend updated with API URL
- [ ] CloudWatch logs verified
- [ ] Cost monitoring enabled

---

## 🐛 Troubleshooting

### **Lambda timeout**

```yaml
# In template.yaml, increase timeout
Globals:
  Function:
    Timeout: 900  # 15 minutes max
```

### **Memory issues**

```yaml
# In template.yaml, increase memory
Globals:
  Function:
    MemorySize: 3008  # Up to 10GB
```

### **Cold start optimization**

```python
# Use provisioned concurrency
aws lambda put-provisioned-concurrency-config \
  --function-name mediquery-api \
  --provisioned-concurrent-executions 1
```

### **CORS issues**

Already configured in `app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🔄 CI/CD Pipeline (Optional)

### **GitHub Actions**

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to AWS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: aws-actions/setup-sam@v1
      - uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      - run: sam build
        working-directory: backend
      - run: sam deploy --no-confirm-changeset --no-fail-on-empty-changeset
        working-directory: backend
```

---

## 📊 Monitoring

### **CloudWatch Logs**

```bash
# View logs
sam logs -n MediQueryFunction --stack-name mediquery-stack --tail

# Or via AWS Console
# CloudWatch → Log Groups → /aws/lambda/mediquery-api
```

### **Metrics**

- Invocations
- Duration
- Errors
- Throttles
- Concurrent executions

### **Alarms**

```bash
# Create error alarm
aws cloudwatch put-metric-alarm \
  --alarm-name mediquery-errors \
  --alarm-description "Alert on Lambda errors" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --evaluation-periods 1 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold
```

---

## 🎯 Production Best Practices

1. **Use Secrets Manager** for API keys
2. **Enable X-Ray** for distributed tracing
3. **Set up CloudWatch alarms**
4. **Use VPC** for OpenSearch security
5. **Enable API Gateway caching**
6. **Implement rate limiting**
7. **Use CloudFront** for global distribution
8. **Enable WAF** for security

---

## 📚 Additional Resources

- [AWS SAM Documentation](https://docs.aws.amazon.com/serverless-application-model/)
- [AWS Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [FastAPI on Lambda](https://mangum.io/)
- [Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)

---

**Ready to deploy!** Choose your deployment mode and follow the steps above.
