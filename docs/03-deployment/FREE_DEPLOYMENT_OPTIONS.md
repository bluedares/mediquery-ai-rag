# Free/Low-Cost Deployment Options for MediQuery AI

## 🎯 **Your Tech Stack Requirements**

**Backend:**
- FastAPI (Python)
- ChromaDB (vector database)
- File storage (PDFs)
- Environment variables (API keys)

**Frontend:**
- React + Vite
- Static site

**External Services:**
- Anthropic API (Claude)
- AWS Bedrock (optional)

---

## 💰 **Deployment Options Comparison**

### **Option 1: Render.com** ⭐ **RECOMMENDED**

**Cost:** FREE tier available

**What You Get:**
- ✅ Free web service (backend)
- ✅ Free static site (frontend)
- ✅ 750 hours/month free
- ✅ Automatic HTTPS
- ✅ GitHub auto-deploy
- ✅ Environment variables
- ✅ Persistent disk (for ChromaDB)

**Limitations:**
- Sleeps after 15 min inactivity (free tier)
- 512 MB RAM
- Slower cold starts

**Setup:**
```yaml
# Backend (render.yaml)
services:
  - type: web
    name: mediquery-backend
    env: python
    buildCommand: "cd backend && pip install -r requirements.txt"
    startCommand: "cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: ANTHROPIC_API_KEY
        sync: false
      - key: USE_CHROMADB
        value: true
    disk:
      name: chromadb-data
      mountPath: /opt/render/project/src/chroma_data
      sizeGB: 1

  - type: web
    name: mediquery-frontend
    env: static
    buildCommand: "cd frontend && npm install && npm run build"
    staticPublishPath: frontend/dist
```

**Pros:**
- ✅ Easiest setup
- ✅ Free tier generous
- ✅ Persistent storage for ChromaDB
- ✅ Auto-deploy from GitHub

**Cons:**
- ❌ Sleeps on inactivity
- ❌ Limited RAM

**Best For:** Demo, portfolio, low-traffic apps

---

### **Option 2: Railway.app** ⭐ **GOOD ALTERNATIVE**

**Cost:** $5/month credit (free trial)

**What You Get:**
- ✅ Backend + Frontend hosting
- ✅ Persistent volumes
- ✅ No sleep on inactivity
- ✅ Better performance than Render free
- ✅ GitHub auto-deploy

**Limitations:**
- $5/month after trial
- Pay-as-you-go after credit

**Setup:**
```yaml
# railway.json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

**Pros:**
- ✅ Better performance
- ✅ No sleep
- ✅ Easy setup

**Cons:**
- ❌ Not truly free (trial only)
- ❌ Costs after $5 credit

**Best For:** Production-ready apps, willing to pay small amount

---

### **Option 3: Vercel (Frontend) + Render (Backend)**

**Cost:** FREE

**What You Get:**
- ✅ Vercel: Best React hosting (free)
- ✅ Render: Backend hosting (free)
- ✅ Automatic HTTPS
- ✅ GitHub auto-deploy

**Setup:**

**Frontend (Vercel):**
```json
// vercel.json
{
  "buildCommand": "cd frontend && npm run build",
  "outputDirectory": "frontend/dist",
  "framework": "vite"
}
```

**Backend (Render):**
- Same as Option 1

**Pros:**
- ✅ Best frontend performance (Vercel CDN)
- ✅ Completely free
- ✅ Separate scaling

**Cons:**
- ❌ Two platforms to manage
- ❌ Backend still sleeps (Render free)

**Best For:** Portfolio projects, best frontend performance

---

### **Option 4: Fly.io**

**Cost:** FREE tier ($5 credit/month)

**What You Get:**
- ✅ 3 shared VMs free
- ✅ Persistent volumes
- ✅ Global deployment
- ✅ No sleep

**Limitations:**
- Credit card required
- More complex setup

**Setup:**
```toml
# fly.toml
app = "mediquery-ai"

[build]
  builder = "paketobuildpacks/builder:base"

[env]
  PORT = "8000"

[[services]]
  http_checks = []
  internal_port = 8000
  protocol = "tcp"

  [[services.ports]]
    port = 80
    handlers = ["http"]

  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]

[mounts]
  source = "chromadb_data"
  destination = "/app/chroma_data"
```

**Pros:**
- ✅ Better free tier than Render
- ✅ No sleep
- ✅ Global edge network

**Cons:**
- ❌ Requires credit card
- ❌ More complex setup

**Best For:** Production apps, global audience

---

### **Option 5: Hugging Face Spaces**

**Cost:** FREE

**What You Get:**
- ✅ Free GPU/CPU hosting
- ✅ Persistent storage
- ✅ GitHub integration
- ✅ Community visibility

**Limitations:**
- Designed for ML demos
- Limited customization
- Public by default

**Setup:**
```python
# app.py (Gradio interface)
import gradio as gr

def query_document(question, file):
    # Your RAG logic here
    return answer

demo = gr.Interface(
    fn=query_document,
    inputs=[gr.Textbox(label="Question"), gr.File(label="Upload PDF")],
    outputs=gr.Textbox(label="Answer")
)

demo.launch()
```

**Pros:**
- ✅ Completely free
- ✅ ML-focused community
- ✅ Easy setup

**Cons:**
- ❌ Limited to Gradio/Streamlit UI
- ❌ Not suitable for production
- ❌ Public by default

**Best For:** ML demos, research projects

---

### **Option 6: PythonAnywhere**

**Cost:** FREE tier

**What You Get:**
- ✅ Free Python web app
- ✅ Persistent storage
- ✅ Always on (free tier)

**Limitations:**
- Limited to 512 MB storage
- No custom domains (free)
- Slower performance

**Pros:**
- ✅ Simple Python hosting
- ✅ No sleep

**Cons:**
- ❌ Limited features
- ❌ Old-school interface
- ❌ No modern CI/CD

**Best For:** Simple Python apps, learning

---

## 🏆 **Recommendation Matrix**

| Use Case | Best Option | Cost | Complexity |
|----------|-------------|------|------------|
| **Demo/Portfolio** | Render.com | Free | Easy ⭐ |
| **Production (Low Traffic)** | Railway.app | $5/mo | Easy |
| **Production (High Traffic)** | Fly.io | Free tier | Medium |
| **Best Frontend** | Vercel + Render | Free | Easy |
| **ML Demo** | Hugging Face | Free | Easy |
| **Learning** | PythonAnywhere | Free | Easy |

---

## 🎯 **My Recommendation for You: Render.com**

**Why:**
1. ✅ **Completely FREE** for your use case
2. ✅ **Easy setup** - Deploy in 10 minutes
3. ✅ **Persistent storage** for ChromaDB
4. ✅ **Auto-deploy** from GitHub
5. ✅ **Environment variables** for API keys
6. ✅ **Good for demos** and portfolio

**Trade-offs:**
- Backend sleeps after 15 min (first request takes ~30s to wake)
- Limited to 512 MB RAM
- Good enough for demo/portfolio

---

## 📋 **Deployment Steps (Render.com)**

### **1. Prepare Your Code**

**Create `render.yaml` in project root:**
```yaml
services:
  # Backend Service
  - type: web
    name: mediquery-backend
    env: python
    region: oregon
    plan: free
    buildCommand: "cd backend && pip install -r requirements.txt"
    startCommand: "cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: ANTHROPIC_API_KEY
        sync: false
      - key: USE_CHROMADB
        value: "true"
      - key: CHROMADB_PERSIST_DIRECTORY
        value: "/opt/render/project/src/chroma_data"
    disk:
      name: chromadb-data
      mountPath: /opt/render/project/src/chroma_data
      sizeGB: 1

  # Frontend Service
  - type: web
    name: mediquery-frontend
    env: static
    region: oregon
    plan: free
    buildCommand: "cd frontend && npm install && npm run build"
    staticPublishPath: frontend/dist
    envVars:
      - key: VITE_API_URL
        value: https://mediquery-backend.onrender.com
```

### **2. Update Frontend API URL**

**Create `frontend/.env.production`:**
```bash
VITE_API_URL=https://mediquery-backend.onrender.com
```

**Update `frontend/src/App.jsx`:**
```javascript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
```

### **3. Deploy to Render**

1. Go to https://render.com
2. Sign up with GitHub
3. Click "New" → "Blueprint"
4. Connect your GitHub repo
5. Render auto-detects `render.yaml`
6. Add environment variables:
   - `ANTHROPIC_API_KEY` = your_key
7. Click "Apply"
8. Wait 5-10 minutes for deployment

### **4. Access Your App**

- **Backend:** `https://mediquery-backend.onrender.com`
- **Frontend:** `https://mediquery-frontend.onrender.com`

---

## 💡 **Cost Optimization Tips**

### **For Free Tier:**
1. **Use ChromaDB** instead of OpenSearch (no AWS costs)
2. **Direct Anthropic API** instead of Bedrock (simpler)
3. **Render free tier** for both services
4. **Accept sleep on inactivity** (demo use case)

### **If Willing to Pay ($5-10/month):**
1. **Railway.app** - No sleep, better performance
2. **Vercel Pro** - Better frontend performance
3. **Fly.io** - Global deployment

### **Production Ready ($20-50/month):**
1. **Railway.app** or **Fly.io** - Backend
2. **Vercel Pro** - Frontend
3. **AWS S3** - File storage
4. **Consider AWS Bedrock** - Better security

---

## 🚀 **Next Steps**

1. **Choose platform** (Render.com recommended)
2. **Create `render.yaml`** in project root
3. **Update frontend API URL**
4. **Push to GitHub**
5. **Connect to Render**
6. **Deploy!**

---

## 📊 **Estimated Costs**

| Option | Monthly Cost | Best For |
|--------|--------------|----------|
| **Render Free** | $0 | Demo, Portfolio |
| **Railway** | $5-10 | Low traffic production |
| **Fly.io** | $0-10 | Medium traffic |
| **Vercel + Render** | $0 | Best free option |
| **Full Production** | $20-50 | High traffic, enterprise |

---

## ⚠️ **Important Notes**

**For Free Tier:**
- Backend sleeps after 15 min inactivity
- First request after sleep takes ~30s
- Good for demos, not production
- Limited RAM (512 MB)

**For Production:**
- Consider paid tier ($7-10/month)
- No sleep, better performance
- More RAM, better reliability

---

## 🎯 **Recommendation Summary**

**For Your Use Case (Demo/Portfolio):**

✅ **Use Render.com FREE tier**
- Easy setup
- GitHub auto-deploy
- Persistent ChromaDB storage
- Good enough for demos
- Completely free

**Deployment Time:** 10-15 minutes  
**Monthly Cost:** $0  
**Maintenance:** Minimal (auto-deploy)

**Ready to deploy? I can help you create the deployment files!**
