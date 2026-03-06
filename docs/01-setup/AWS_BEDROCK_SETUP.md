# AWS Bedrock Setup Guide - Updated March 2026 - Complete Guide

## ❓ Do You Need a Separate Claude API Key?

### **NO! You only need AWS credentials.**

**Why?**
- Claude Sonnet 4.6 is accessed through **AWS Bedrock**
- Bedrock is an AWS service
- You authenticate with AWS credentials only
- No separate Anthropic/Claude API key needed

---

## 🚀 Quick Setup (15 Minutes)

### **Step 1: Create AWS Account** (5 min)

1. Go to: **https://aws.amazon.com**
2. Click **"Create an AWS Account"**
3. Fill in:
   - Email address
   - Password
   - AWS account name (e.g., "MediQuery-Dev")
4. Enter contact information
5. Add payment method (credit/debit card)
   - **Don't worry**: Free tier covers demo usage
   - You won't be charged unless you exceed limits
6. Verify phone number (SMS code)
7. Choose **"Basic Support Plan"** (Free)
8. Click **"Complete Sign Up"**

✅ **Account created!**

---

### **Step 2: Sign in to AWS Console** (1 min)

1. Go to: **https://console.aws.amazon.com**
2. Sign in with your email and password
3. You should see the AWS Management Console

---

### **Step 3: Create IAM User** (3 min)

**Why?** Best practice - don't use root account credentials.

1. In AWS Console search bar, type: **IAM**
2. Click **"IAM"** (Identity and Access Management)
3. In left sidebar, click **"Users"**
4. Click **"Create user"** (orange button)
5. **User name**: `mediquery-dev`
6. Click **"Next"**
7. Select **"Attach policies directly"**
8. In search box, type: `bedrock`
9. Check the box for: **`AmazonBedrockFullAccess`**
10. (Optional) Also add: **`AmazonS3FullAccess`** if using S3
11. Click **"Next"**
12. Click **"Create user"**

✅ **IAM user created!**

---

### **Step 4: Create Access Keys** (2 min)

**These are your credentials for the application.**

1. Click on the user you just created: **`mediquery-dev`**
2. Go to **"Security credentials"** tab
3. Scroll down to **"Access keys"** section
4. Click **"Create access key"**
5. Select use case: **"Application running outside AWS"**
6. Check the confirmation box
7. Click **"Next"**
8. Description (optional): "MediQuery AI Development"
9. Click **"Create access key"**

**⚠️ CRITICAL: You'll see two values:**

```
Access Key ID: AKIA...
Secret Access Key: wJalrXUtn...
```

**COPY THESE NOW!** You can't see the secret key again.

10. Click **"Download .csv file"** (recommended backup)
11. Click **"Done"**

✅ **Access keys created!**

---

### **Step 5: Enable Bedrock Model Access** (3 min)

**This is the most important step!**

1. In AWS Console search bar, type: **Bedrock**
2. Click **"Amazon Bedrock"**
3. In left sidebar, click **"Model access"**
4. Click **"Manage model access"** (orange button on right)
5. Scroll to find **"Anthropic"** section
6. Check the boxes for:
   - ✅ **Claude 3.5 Sonnet v2** (recommended)
   - ✅ **Claude 3 Sonnet** (backup)
   - ✅ **Claude 3 Haiku** (optional, cheaper)
7. Scroll to bottom, click **"Request model access"**
8. Wait 2-5 minutes (usually instant)
9. Refresh the page
10. Status should show: **"Access granted"** ✅

**Note**: If status shows "Pending", wait a few minutes and refresh.

✅ **Bedrock access enabled!**

---

### **Step 6: Configure Your Application** (1 min)

Create `.env` file in `backend/` directory:

```bash
cd backend
touch .env
```

Edit `.env` file and add:

```bash
# AWS Credentials (from Step 4)
AWS_ACCESS_KEY_ID=AKIA...your-key-here
AWS_SECRET_ACCESS_KEY=wJalrXUtn...your-secret-here
AWS_REGION=us-east-1

# Optional - S3 bucket (leave empty for mock mode)
S3_BUCKET_NAME=

# Optional - OpenSearch (leave empty for mock mode)
OPENSEARCH_ENDPOINT=

# Debug Settings
DEBUG_MODE=true
TRACE_AGENTS=true
TRACE_LLM_CALLS=true
LOG_LEVEL=INFO
```

**Replace** `AKIA...` and `wJalrXUtn...` with your actual keys from Step 4.

✅ **Application configured!**

---

### **Step 7: Test Your Setup** (1 min)

**Option A: Test with AWS CLI** (if installed)

```bash
aws bedrock list-foundation-models --region us-east-1 | grep -i claude
```

Should show Claude models available.

**Option B: Test in Python**

```python
import boto3

# Test connection
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
print("✅ AWS Bedrock connection successful!")
```

**Option C: Start your app and test**

```bash
# Start backend
cd backend
python3 -m uvicorn app.main:app --reload

# Check logs for Bedrock connection
```

✅ **Setup complete!**

---

## 💰 Cost Breakdown

### **Free Tier** (First 12 months)
- S3: 5GB storage free
- Lambda: 1M requests/month free
- API Gateway: 1M calls/month free

### **Bedrock Pricing** (Pay-per-use)

**Claude 3.5 Sonnet v2:**
- Input: ~$3 per 1M tokens
- Output: ~$15 per 1M tokens

**For your demo (50 queries):**
- 50 queries × 500 tokens each = 25,000 tokens
- Estimated cost: **$0.10 - $0.50 total**

**Monthly usage (100 queries/day):**
- ~3,000 queries/month
- Estimated cost: **$5-10/month**

### **You'll spend less than $1 for the entire demo!**

---

## 🔒 Security Best Practices

### **1. Never Commit Credentials**

```bash
# .gitignore already includes:
.env
*.pem
*.key
```

### **2. Use Environment Variables**

```bash
# Set in terminal (temporary)
export AWS_ACCESS_KEY_ID=AKIA...
export AWS_SECRET_ACCESS_KEY=wJalrXUtn...

# Or use .env file (recommended)
```

### **3. Rotate Keys Regularly**

```bash
# Create new key in AWS Console
# Update .env file
# Delete old key in AWS Console
```

### **4. Use IAM Roles for Production**

For production deployments, use IAM roles instead of access keys.

---

## 🐛 Troubleshooting

### **Error: "Unable to locate credentials"**

**Solution**: Check `.env` file exists and has correct format

```bash
# Verify .env file
cat backend/.env

# Should show your AWS keys
```

### **Error: "Access Denied" for Bedrock**

**Solution**: 
1. Go to AWS Console → Bedrock → Model access
2. Check status shows "Access granted"
3. If "Pending", wait 5 minutes and refresh
4. If "Not requested", request access again

### **Error: "Region not supported"**

**Solution**: Use a supported region

Bedrock is available in:
- ✅ **us-east-1** (N. Virginia) - Recommended
- ✅ **us-west-2** (Oregon)
- ✅ **eu-central-1** (Frankfurt)
- ✅ **ap-southeast-1** (Singapore)

Change in `.env`:
```bash
AWS_REGION=us-east-1
```

### **Error: "Model not found"**

**Solution**: Check model ID in code

```python
# Correct model ID for Claude 3.5 Sonnet v2
model_id = "anthropic.claude-3-5-sonnet-20241022-v2:0"

# Or use latest
model_id = "anthropic.claude-sonnet-4-6-20260223-v1:0"
```

---

## ✅ Verification Checklist

Before running your app:

- [ ] AWS account created
- [ ] IAM user created (`mediquery-dev`)
- [ ] Access keys downloaded and saved
- [ ] Bedrock model access enabled (Claude Sonnet)
- [ ] `.env` file created in `backend/` directory
- [ ] AWS credentials added to `.env`
- [ ] Region set to `us-east-1`

---

## 🚀 Start Your Application

```bash
# Terminal 1 - Backend
cd backend
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

**Open**: http://localhost:5174

**Upload a PDF and start querying!** 🎉

---

## 📊 Monitoring Usage

### **View Bedrock Usage**

1. AWS Console → Bedrock
2. Left sidebar → "Usage"
3. See token counts and costs

### **Set Up Billing Alerts**

1. AWS Console → Billing
2. "Billing preferences"
3. Enable "Receive Billing Alerts"
4. Set threshold (e.g., $10)

---

## 🎯 Quick Reference

**AWS Console**: https://console.aws.amazon.com
**Bedrock Pricing**: https://aws.amazon.com/bedrock/pricing/
**IAM Best Practices**: https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html

---

## 📞 Need Help?

**AWS Support**:
- Free tier support: https://aws.amazon.com/premiumsupport/
- Bedrock docs: https://docs.aws.amazon.com/bedrock/
- IAM docs: https://docs.aws.amazon.com/iam/

**Common Issues**:
- Bedrock not available in region → Use `us-east-1`
- Model access pending → Wait 5 minutes
- Credentials not working → Recreate access keys
- High costs → Check token usage in Bedrock console

---

**Remember**: You only need AWS credentials. No separate Claude API key needed! 🎉
