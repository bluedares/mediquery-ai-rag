# AWS Setup Guide for MediQuery AI

## 🔑 Required AWS Credentials

You need AWS credentials to use:
1. **AWS Bedrock** - For Claude Sonnet 4.6 LLM
2. **AWS S3** - For document storage
3. **AWS OpenSearch** - For vector search (optional for demo)

---

## 📋 Step-by-Step AWS Setup

### **Option 1: Quick Demo Setup (Recommended for Interview)**

For the interview demo, you can run in **mock mode** without AWS credentials. The system will simulate responses.

**Skip AWS setup and use mock mode** ✅

---

### **Option 2: Full AWS Setup (Production)**

#### **Step 1: Create AWS Account**

1. Go to https://aws.amazon.com
2. Click "Create an AWS Account"
3. Follow the signup process
4. **Note**: Requires credit card, but has free tier

#### **Step 2: Create IAM User**

1. Log into AWS Console
2. Go to **IAM** (Identity and Access Management)
3. Click **Users** → **Add users**
4. User name: `mediquery-dev`
5. Select: **Programmatic access**
6. Click **Next: Permissions**

#### **Step 3: Attach Policies**

Attach these policies:
- ✅ `AmazonBedrockFullAccess` - For Claude Sonnet 4.6
- ✅ `AmazonS3FullAccess` - For document storage
- ✅ `AmazonOpenSearchServiceFullAccess` - For vector search

Click **Next** → **Create user**

#### **Step 4: Save Credentials**

**IMPORTANT**: Download and save these credentials:
```
Access Key ID: AKIA...
Secret Access Key: wJalrXUtn...
```

⚠️ **You'll only see the secret key once!**

#### **Step 5: Enable Bedrock Model Access**

1. Go to **AWS Bedrock** console
2. Click **Model access** (left sidebar)
3. Click **Manage model access**
4. Find **Anthropic** section
5. Enable: `Claude 3.5 Sonnet v2` or `Claude Sonnet 4` (if available)
6. Click **Save changes**
7. Wait 2-5 minutes for approval (usually instant)

#### **Step 6: Configure Backend**

Create `.env` file in `backend/` directory:

```bash
# AWS Credentials
AWS_ACCESS_KEY_ID=AKIA...your-key-here
AWS_SECRET_ACCESS_KEY=wJalrXUtn...your-secret-here
AWS_REGION=us-east-1

# AWS Services
S3_BUCKET_NAME=mediquery-documents
OPENSEARCH_ENDPOINT=  # Leave empty for mock mode

# Debug Settings
DEBUG_MODE=true
TRACE_AGENTS=true
TRACE_LLM_CALLS=true
```

#### **Step 7: Create S3 Bucket (Optional)**

```bash
# Using AWS CLI
aws s3 mb s3://mediquery-documents --region us-east-1
```

Or via AWS Console:
1. Go to **S3**
2. Click **Create bucket**
3. Name: `mediquery-documents`
4. Region: `us-east-1`
5. Click **Create bucket**

---

## 🚀 Quick Start Commands

### **Install AWS CLI** (Optional but helpful)

```bash
# macOS
brew install awscli

# Verify installation
aws --version
```

### **Configure AWS CLI**

```bash
aws configure

# Enter when prompted:
AWS Access Key ID: AKIA...
AWS Secret Access Key: wJalrXUtn...
Default region name: us-east-1
Default output format: json
```

### **Test Bedrock Access**

```bash
# List available models
aws bedrock list-foundation-models --region us-east-1

# Test Claude Sonnet invocation
aws bedrock-runtime invoke-model \
  --model-id anthropic.claude-sonnet-4-6-20260223-v1:0 \
  --body '{"prompt":"Hello","max_tokens":100}' \
  --region us-east-1 \
  response.json
```

---

## 💰 Cost Estimates

### **Free Tier** (First 12 months)
- ✅ S3: 5GB storage, 20,000 GET requests
- ✅ Lambda: 1M requests/month

### **Bedrock Pricing** (Pay-per-use)
- Claude Sonnet 4.6:
  - Input: ~$3 per 1M tokens
  - Output: ~$15 per 1M tokens
- **Demo cost**: ~$0.10-0.50 for 50-100 queries

### **OpenSearch** (Optional)
- Small instance: ~$0.10/hour (~$70/month)
- **For demo**: Use mock mode (free)

---

## 🔒 Security Best Practices

### **1. Never Commit Credentials**

```bash
# .gitignore already includes:
.env
*.pem
*.key
```

### **2. Use IAM Roles in Production**

Instead of access keys, use:
- EC2 Instance Roles
- Lambda Execution Roles
- ECS Task Roles

### **3. Rotate Keys Regularly**

```bash
# Create new access key
aws iam create-access-key --user-name mediquery-dev

# Delete old key
aws iam delete-access-key --access-key-id AKIA... --user-name mediquery-dev
```

### **4. Use AWS Secrets Manager** (Production)

```python
import boto3

secrets = boto3.client('secretsmanager')
secret = secrets.get_secret_value(SecretId='mediquery/api-keys')
```

---

## 🧪 Testing Without AWS (Mock Mode)

The application works in **mock mode** without AWS credentials:

1. **Don't create `.env` file** (or leave AWS keys empty)
2. Services will detect missing credentials
3. Mock responses will be returned
4. Perfect for development and demos!

**Mock Mode Features:**
- ✅ Simulated LLM responses
- ✅ Fake document storage
- ✅ Mock vector search results
- ✅ All UI features work
- ✅ Agent workflow visualization works

---

## 🐛 Troubleshooting

### **Error: "Unable to locate credentials"**

**Solution**: 
```bash
# Check if credentials are set
aws configure list

# Or set environment variables
export AWS_ACCESS_KEY_ID=AKIA...
export AWS_SECRET_ACCESS_KEY=wJalrXUtn...
export AWS_REGION=us-east-1
```

### **Error: "Access Denied" for Bedrock**

**Solution**:
1. Check model access in Bedrock console
2. Verify IAM permissions include `AmazonBedrockFullAccess`
3. Wait 5 minutes after enabling model access

### **Error: "Region not supported"**

**Solution**:
Bedrock is available in these regions:
- `us-east-1` (N. Virginia) ✅ Recommended
- `us-west-2` (Oregon)
- `eu-central-1` (Frankfurt)

Change region in `.env`:
```bash
AWS_REGION=us-east-1
```

---

## 📝 Environment Variables Reference

### **Required for Production**
```bash
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=wJalrXUtn...
AWS_REGION=us-east-1
```

### **Optional**
```bash
S3_BUCKET_NAME=mediquery-documents
OPENSEARCH_ENDPOINT=https://...es.amazonaws.com
BEDROCK_MODEL_ID=anthropic.claude-sonnet-4-6-20260223-v1:0
```

### **Debug Settings**
```bash
DEBUG_MODE=true
TRACE_AGENTS=true
TRACE_LLM_CALLS=true
LOG_LEVEL=DEBUG
```

---

## ✅ Verification Checklist

Before running the application:

- [ ] AWS account created
- [ ] IAM user created with programmatic access
- [ ] Policies attached (Bedrock, S3, OpenSearch)
- [ ] Access keys downloaded and saved
- [ ] Bedrock model access enabled
- [ ] `.env` file created with credentials
- [ ] AWS CLI configured (optional)
- [ ] Tested Bedrock access (optional)

---

## 🎯 For Interview Demo

**Recommended approach:**

1. **Use Mock Mode** - No AWS setup needed
2. Explain: "In production, this would connect to AWS Bedrock"
3. Show the code that handles AWS integration
4. Discuss cost optimization and security

**If you have AWS credits:**

1. Set up minimal AWS (just Bedrock)
2. Skip OpenSearch (use mock mode)
3. Skip S3 (use mock mode)
4. Show real Claude Sonnet 4.6 responses

---

## 📞 Need Help?

- AWS Documentation: https://docs.aws.amazon.com/bedrock
- Bedrock Pricing: https://aws.amazon.com/bedrock/pricing
- Free Tier: https://aws.amazon.com/free

---

**Next Steps**: Choose your setup option and follow the steps above!
