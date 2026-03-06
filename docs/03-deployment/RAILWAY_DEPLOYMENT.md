# Railway.app Deployment Guide

## Prerequisites
- Railway.app account (you already have this)
- GitHub repository connected to Railway
- Environment variables ready

## Backend Deployment Steps

### 1. Create New Project on Railway

1. Go to [railway.app](https://railway.app)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repository: `mediquery-ai-rag`
5. Railway will auto-detect the `Dockerfile`

### 2. Configure Environment Variables

Add these environment variables in Railway dashboard:

**Required:**
```
ANTHROPIC_API_KEY=your_anthropic_api_key_here
USE_DIRECT_ANTHROPIC=true
USE_CHROMADB=true
CHROMADB_PERSIST_DIRECTORY=./chroma_data
```

**Optional (AWS - if you want to use Bedrock later):**
```
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
S3_BUCKET_NAME=mediquery-documents
OPENSEARCH_ENDPOINT=
```

### 3. Deploy

1. Railway will automatically start building using the `Dockerfile`
2. Build time: ~5-10 minutes (first time)
3. Subsequent deploys: ~2-3 minutes (cached layers)

### 4. Get Your Backend URL

After deployment:
1. Go to your service in Railway
2. Click **"Settings"** → **"Networking"**
3. Click **"Generate Domain"**
4. Copy the URL (e.g., `https://mediquery-backend-production.up.railway.app`)

### 5. Update Frontend Environment

Update `frontend/.env.production`:
```
VITE_API_URL=https://your-railway-backend-url.up.railway.app
```

## Frontend Deployment (Vercel/Netlify)

### Option 1: Vercel (Recommended)

1. Go to [vercel.com](https://vercel.com)
2. Click **"New Project"**
3. Import your GitHub repo
4. Configure:
   - **Framework Preset:** Vite
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
5. Add environment variable:
   - `VITE_API_URL` = your Railway backend URL
6. Deploy

### Option 2: Netlify

1. Go to [netlify.com](https://netlify.com)
2. Click **"Add new site"** → **"Import an existing project"**
3. Choose your GitHub repo
4. Configure:
   - **Base directory:** `frontend`
   - **Build command:** `npm run build`
   - **Publish directory:** `frontend/dist`
5. Add environment variable:
   - `VITE_API_URL` = your Railway backend URL
6. Deploy

## Advantages of Railway over Render

✅ **Faster builds** - Better caching, 2-3 min vs 30 min
✅ **Better free tier** - $5 free credit/month
✅ **Persistent volumes** - ChromaDB data persists
✅ **No cold starts** - Service stays warm
✅ **Better logs** - Real-time, searchable
✅ **Simpler config** - Just Dockerfile + railway.json

## Monitoring

### Health Check
```bash
curl https://your-railway-url.up.railway.app/health
```

### Logs
- View real-time logs in Railway dashboard
- Click on your service → **"Deployments"** → **"View Logs"**

## Troubleshooting

### Build Fails
- Check Dockerfile syntax
- Verify `requirements-minimal.txt` exists
- Check Railway build logs

### App Crashes on Start
- Verify environment variables are set
- Check that `ANTHROPIC_API_KEY` is valid
- Review application logs

### ChromaDB Data Lost
- Railway automatically persists volumes
- Data in `/app/chroma_data` is preserved across deploys

## Cost Estimation

**Free Tier:**
- $5 credit/month
- ~500 hours of uptime
- Should be sufficient for demo/development

**Paid (if needed):**
- ~$5-10/month for backend
- Frontend on Vercel/Netlify is free

## Next Steps

1. Deploy backend to Railway
2. Get backend URL
3. Deploy frontend to Vercel/Netlify
4. Test the full application
5. Monitor usage and logs
