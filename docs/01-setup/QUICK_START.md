# MediQuery AI - Quick Start Guide

## 🚀 Two Options to Run the Demo

---

## ✅ **Option 1: Mock Mode (No AWS Required)** - RECOMMENDED FOR DEMO

Perfect for interview demo - works immediately without any setup!

### Steps:

1. **Backend is already running** ✅
   - URL: http://localhost:8000
   - Status: Check http://localhost:8000/health

2. **Frontend is already running** ✅
   - URL: http://localhost:5174
   - Just refresh your browser!

3. **Test the application:**
   - Open http://localhost:5174 in your browser
   - Enter a question like: "What are the primary endpoints?"
   - Click "Ask Question"
   - Watch the agent workflow in action!

**What works in Mock Mode:**
- ✅ Full UI with agent visualization
- ✅ Simulated AI responses
- ✅ Citation display
- ✅ Agent workflow trace
- ✅ All frontend features
- ✅ Perfect for demonstrating architecture

**What's simulated:**
- LLM responses (uses placeholder text)
- Vector search (returns mock results)
- Document storage (simulated)

---

## 🔑 **Option 2: Full AWS Setup (Real Claude Sonnet 4.6)**

For production-quality demo with real AI responses.

### Required AWS Services:

1. **AWS Bedrock** - For Claude Sonnet 4.6 ✅ REQUIRED
2. **AWS S3** - For document storage (optional, can use mock)
3. **AWS OpenSearch** - For vector search (optional, can use mock)

### Quick Setup Steps:

#### **1. Create AWS Account**
- Go to https://aws.amazon.com
- Sign up (requires credit card, but has free tier)

#### **2. Get AWS Credentials**

```bash
# Go to AWS Console → IAM → Users → Create User
# Name: mediquery-dev
# Access type: Programmatic access
# Permissions: AmazonBedrockFullAccess

# You'll get:
Access Key ID: AKIA...
Secret Access Key: wJalrXUtn...
```

#### **3. Enable Bedrock Model**

- Go to AWS Bedrock Console
- Click "Model access"
- Enable "Claude 3.5 Sonnet" or "Claude Sonnet 4"
- Wait 2-5 minutes for approval

#### **4. Create .env File**

Create `backend/.env`:

```bash
# AWS Credentials
AWS_ACCESS_KEY_ID=AKIA...your-key-here
AWS_SECRET_ACCESS_KEY=wJalrXUtn...your-secret-here
AWS_REGION=us-east-1

# Optional (can leave empty for mock mode)
S3_BUCKET_NAME=
OPENSEARCH_ENDPOINT=

# Debug
DEBUG_MODE=true
TRACE_AGENTS=true
TRACE_LLM_CALLS=true
```

#### **5. Restart Backend**

```bash
# Kill current backend
pkill -f uvicorn

# Start with new credentials
cd backend
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### **6. Test**

- Frontend: http://localhost:5174
- Ask a question
- Get real Claude Sonnet 4.6 responses!

---

## 💰 Cost Estimate

**Bedrock (Claude Sonnet 4.6):**
- ~$3 per 1M input tokens
- ~$15 per 1M output tokens
- **Demo cost**: $0.10 - $0.50 for 50-100 queries

**Free Tier:**
- S3: 5GB storage free
- Lambda: 1M requests/month free

---

## 🎯 Recommended for Interview

**Use Mock Mode!** Here's why:

1. ✅ **No setup time** - works immediately
2. ✅ **No cost** - completely free
3. ✅ **No AWS account needed**
4. ✅ **Shows architecture** - demonstrates the design
5. ✅ **Explains well** - "In production, this connects to AWS Bedrock"

During interview, you can:
- Show the working UI
- Explain the multi-agent architecture
- Walk through the code
- Discuss AWS integration
- Highlight production-ready features

---

## 🔍 Verify Everything is Running

```bash
# Check backend
curl http://localhost:8000/health

# Should return: {"status":"healthy",...}

# Check frontend
curl http://localhost:5174

# Should return HTML
```

---

## 🐛 Troubleshooting

### Frontend shows blank page?

```bash
# Restart frontend
cd frontend
npm run dev
```

### Backend not responding?

```bash
# Check if running
ps aux | grep uvicorn

# Restart if needed
cd backend
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Port already in use?

```bash
# Kill processes
pkill -f uvicorn
pkill -f vite

# Restart both servers
```

---

## 📱 Access URLs

- **Frontend**: http://localhost:5174
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 🎬 Ready to Demo!

1. Open http://localhost:5174
2. Enter a question
3. Watch the magic happen! ✨

**For detailed AWS setup**: See `AWS_SETUP_GUIDE.md`
**For demo script**: See `DEMO_GUIDE.md`
