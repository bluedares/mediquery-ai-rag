# Render.com Deployment Guide

## 🚀 **Quick Deployment Steps**

Your code is ready to deploy! Follow these steps:

---

## 📋 **Prerequisites**

✅ GitHub account  
✅ Anthropic API key  
✅ Code pushed to GitHub  

---

## 🎯 **Step-by-Step Deployment**

### **Step 1: Sign Up for Render.com**

1. Go to https://render.com
2. Click **"Get Started"**
3. Sign up with your GitHub account
4. Authorize Render to access your repositories

---

### **Step 2: Create New Blueprint**

1. Click **"New"** → **"Blueprint"**
2. Connect your repository: `bluedares/mediquery-ai-rag`
3. Render will automatically detect `render.yaml`
4. Click **"Apply"**

---

### **Step 3: Configure Environment Variables**

Render will prompt you to add environment variables:

**Required:**
- **ANTHROPIC_API_KEY** = `your_anthropic_api_key_here`

**Already Set (from render.yaml):**
- USE_DIRECT_ANTHROPIC = `true`
- USE_CHROMADB = `true`
- CHROMADB_PERSIST_DIRECTORY = `/opt/render/project/src/chroma_data`

Click **"Apply"** to start deployment.

---

### **Step 4: Wait for Deployment**

**Backend deployment:**
- Installing Python dependencies (~3 minutes)
- Starting FastAPI server
- Status: ✅ Live at `https://mediquery-backend.onrender.com`

**Frontend deployment:**
- Installing npm packages (~2 minutes)
- Building React app
- Status: ✅ Live at `https://mediquery-frontend.onrender.com`

**Total time:** ~5-10 minutes

---

### **Step 5: Verify Deployment**

**Test Backend:**
```bash
curl https://mediquery-backend.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-03-06T12:00:00Z",
  "version": "1.0.0"
}
```

**Test Frontend:**
Open in browser: https://mediquery-frontend.onrender.com

---

## 🎉 **Your App is Live!**

**Frontend:** https://mediquery-frontend.onrender.com  
**Backend API:** https://mediquery-backend.onrender.com  
**API Docs:** https://mediquery-backend.onrender.com/docs  

---

## ⚙️ **Post-Deployment Configuration**

### **Update Frontend URL (if needed)**

If your backend URL is different, update `frontend/.env.production`:

```bash
VITE_API_URL=https://your-backend-url.onrender.com
```

Then redeploy frontend:
```bash
git add frontend/.env.production
git commit -m "Update API URL"
git push
```

Render will auto-deploy the changes.

---

## 🔧 **Troubleshooting**

### **Backend fails to start**

**Check logs:**
1. Go to Render dashboard
2. Click on `mediquery-backend`
3. View **"Logs"** tab

**Common issues:**
- Missing ANTHROPIC_API_KEY
- Python dependency errors
- Port binding issues

**Solution:**
```bash
# Ensure environment variables are set
# Check render.yaml configuration
# Verify requirements.txt is complete
```

---

### **Frontend shows API errors**

**Check CORS:**
1. Verify backend CORS allows frontend URL
2. Check `backend/app/main.py`:
```python
allow_origins=[
    "https://mediquery-frontend.onrender.com",
]
```

**Check API URL:**
1. Verify `frontend/.env.production`:
```bash
VITE_API_URL=https://mediquery-backend.onrender.com
```

---

### **Backend sleeps after 15 minutes**

**Expected behavior on free tier:**
- Backend sleeps after 15 min inactivity
- First request after sleep takes ~30s to wake up
- Subsequent requests are fast

**Solutions:**
1. **Accept it** - Good for demos
2. **Upgrade to paid** - $7/month, no sleep
3. **Use cron job** - Ping every 14 minutes (not recommended)

---

### **ChromaDB data lost**

**Check persistent disk:**
1. Go to backend service settings
2. Verify disk is mounted at `/opt/render/project/src/chroma_data`
3. Check disk usage in dashboard

**If data is lost:**
- Re-upload documents
- ChromaDB will recreate collections

---

## 📊 **Monitoring**

### **View Logs**

**Backend logs:**
1. Dashboard → `mediquery-backend` → Logs
2. Real-time log streaming
3. Search and filter logs

**Frontend logs:**
1. Dashboard → `mediquery-frontend` → Logs
2. Build logs and deploy logs

---

### **Check Metrics**

**Available metrics:**
- Request count
- Response time
- Error rate
- Memory usage
- CPU usage

**Access:**
Dashboard → Service → Metrics tab

---

## 🔄 **Auto-Deploy from GitHub**

**How it works:**
1. Push code to GitHub
2. Render detects changes
3. Automatically rebuilds and deploys
4. ~5 minutes deployment time

**Disable auto-deploy:**
1. Service settings → Build & Deploy
2. Toggle "Auto-Deploy" off

---

## 💰 **Free Tier Limits**

**What you get:**
- ✅ 750 hours/month (enough for 24/7)
- ✅ 512 MB RAM
- ✅ 1 GB persistent disk
- ✅ Automatic HTTPS
- ✅ Unlimited bandwidth

**Limitations:**
- ⚠️ Sleeps after 15 min inactivity
- ⚠️ Slower cold starts (~30s)
- ⚠️ Limited RAM (512 MB)

---

## 🚀 **Upgrade Options**

### **Starter Plan ($7/month per service)**

**Benefits:**
- ✅ No sleep
- ✅ 512 MB RAM (same)
- ✅ Faster cold starts
- ✅ Custom domains

**Cost for both services:** $14/month

---

### **Standard Plan ($25/month per service)**

**Benefits:**
- ✅ 2 GB RAM
- ✅ Better performance
- ✅ Priority support

**Cost for both services:** $50/month

---

## 📝 **Deployment Checklist**

Before deploying:

✅ Code pushed to GitHub  
✅ `render.yaml` in project root  
✅ Frontend `.env.production` configured  
✅ Backend CORS updated  
✅ `.gitignore` excludes sensitive files  
✅ Anthropic API key ready  

After deploying:

✅ Backend health check passes  
✅ Frontend loads correctly  
✅ Can upload documents  
✅ Can ask questions  
✅ ChromaDB persists data  

---

## 🎯 **Next Steps**

1. **Test your app** - Upload a document and ask questions
2. **Share the link** - Add to portfolio/resume
3. **Monitor usage** - Check Render dashboard
4. **Optimize** - Review logs for errors
5. **Upgrade if needed** - Consider paid tier for production

---

## 📞 **Support**

**Render.com:**
- Docs: https://render.com/docs
- Community: https://community.render.com
- Support: support@render.com

**Your App:**
- GitHub: https://github.com/bluedares/mediquery-ai-rag
- Issues: Create GitHub issue

---

**Your app is now live and ready to share!** 🎉
