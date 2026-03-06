# Render.com Free Tier Limitations

## ⚠️ **Important: ChromaDB Data Persistence**

### **Free Tier Limitation:**
Render.com **free tier does NOT support persistent disks**.

This means:
- ❌ ChromaDB data is stored in **ephemeral storage**
- ❌ Data is **lost when service restarts**
- ❌ Uploads are **lost on sleep/wake cycles**

---

## 🔄 **What Happens:**

### **On Free Tier:**
1. User uploads documents → Stored in ChromaDB
2. Service sleeps after 15 min inactivity
3. Service wakes up on next request
4. **All ChromaDB data is gone** ❌

### **Impact:**
- Documents must be re-uploaded after each sleep
- Good for **demo/testing only**
- **Not suitable for production**

---

## ✅ **Solutions:**

### **Option 1: Accept Data Loss (Demo Only)**
- Use free tier for portfolio/demo
- Re-upload test documents each session
- Perfect for showing functionality
- **Cost: $0/month**

### **Option 2: Upgrade to Starter Plan**
- $7/month per service = $14/month total
- **Persistent disk included** ✅
- Data survives restarts ✅
- No sleep on inactivity ✅
- **Recommended for production**

### **Option 3: Use Alternative Storage**
- Store embeddings in external database
- Use Pinecone (free tier: 1 index)
- Use Supabase with pgvector (free tier available)
- More complex setup

---

## 📊 **Comparison:**

| Feature | Free Tier | Starter ($14/mo) |
|---------|-----------|------------------|
| **Persistent Storage** | ❌ No | ✅ Yes (10 GB) |
| **Data Survives Restart** | ❌ No | ✅ Yes |
| **Sleep After 15 Min** | ✅ Yes | ❌ No |
| **Cold Start Time** | ~30 seconds | Instant |
| **Good For** | Demo/Portfolio | Production |

---

## 🎯 **Recommendation:**

### **For Your Use Case (Demo/Portfolio):**

**Use Free Tier with these workarounds:**

1. **Keep test documents ready** - Re-upload when needed
2. **Use small test PDFs** - Quick to re-upload
3. **Document the limitation** - Explain in README
4. **Show the process** - Upload → Query → Results

**This is perfect for:**
- Portfolio demonstrations
- Interview presentations
- Proof of concept
- Learning and testing

---

## 🚀 **Deployment Strategy:**

### **Phase 1: Free Tier (Now)**
- Deploy with ephemeral storage
- Use for demos and portfolio
- Test all functionality
- **Cost: $0**

### **Phase 2: Upgrade (When Needed)**
- Upgrade to Starter plan
- Add persistent disk
- Production-ready
- **Cost: $14/month**

---

## 📝 **Current Configuration:**

Our `render.yaml` is configured for **free tier**:
- ✅ No disk configuration
- ✅ Ephemeral ChromaDB storage
- ✅ Works for demos
- ⚠️ Data lost on restart

To upgrade later:
1. Change plan to `starter`
2. Add disk configuration
3. Redeploy

---

## 💡 **Workaround for Demos:**

**Keep a "demo script":**

```bash
# Demo preparation
1. Start app: https://mediquery-frontend.onrender.com
2. Upload test document (keep ready)
3. Wait for processing
4. Ask sample questions
5. Show results

# If service was sleeping:
- First request wakes it up (~30s)
- Re-upload document
- Continue demo
```

---

## ⚠️ **Important Notes:**

**Free Tier is NOT for:**
- ❌ Production use
- ❌ Storing user data long-term
- ❌ High-traffic applications
- ❌ Mission-critical apps

**Free Tier IS for:**
- ✅ Demos and portfolios
- ✅ Testing and development
- ✅ Learning and experimentation
- ✅ Proof of concept

---

**For your portfolio/demo purposes, free tier is perfect!** 🎯

Just re-upload test documents when showing the app.
