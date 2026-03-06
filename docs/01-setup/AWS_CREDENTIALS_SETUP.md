# AWS Credentials Setup - Step by Step

## ❓ Do You Need a Separate Claude API Key?

**NO!** ✅ You only need AWS credentials.

**Why?**
- Claude Sonnet 4.6 is accessed through **AWS Bedrock**
- Bedrock is an AWS service
- You use AWS credentials, not Anthropic API keys
- Everything goes through AWS

---

## 🔑 What You Need

**Only ONE thing**: AWS Account with Bedrock access

**You do NOT need:**
- ❌ Anthropic API key
- ❌ OpenAI API key  
- ❌ Separate Claude subscription

---

## 📋 Step-by-Step AWS Setup

### **Step 1: Create AWS Account** (5 minutes)

1. Go to: https://aws.amazon.com
2. Click **"Create an AWS Account"**
3. Fill in:
   - Email address
   - Password
   - AWS account name
4. Enter contact information
5. Add payment method (credit/debit card)
   - **Note**: You won't be charged unless you exceed free tier
6. Verify phone number
7. Choose **Basic Support Plan** (Free)
8. Click **"Complete Sign Up"**

✅ **You now have an AWS account!**

---

### **Step 2: Create IAM User** (3 minutes)

1. Log into AWS Console: https://console.aws.amazon.com
2. Search for **"IAM"** in the top search bar
3. Click **"Users"** in left sidebar
4. Click **"Create user"**
5. User name: `mediquery-dev`
6. Click **"Next"**
7. Select **"Attach policies directly"**
8. Search and select these policies:
   - ✅ `AmazonBedrockFullAccess`
   - ✅ `AmazonS3FullAccess` (optional)
9. Click **"Next"**
10. Click **"Create user"**

---

### **Step 3: Create Access Keys** (2 minutes)

1. Click on the user you just created (`mediquery-dev`)
2. Go to **"Security credentials"** tab
3. Scroll to **"Access keys"**
4. Click **"Create access key"**
5. Select **"Application running outside AWS"**
6. Click **"Next"**
7. Add description: "MediQuery AI Development"
8. Click **"Create access key"**

**⚠️ IMPORTANT**: You'll see:
```
Access Key ID: AKIA...
Secret Access Key: wJalrXUtn...
```

**COPY THESE NOW!** You can't see the secret key again.

9. Click **"Download .csv file"** (recommended)
10. Click **"Done"**

✅ **You now have AWS credentials!**

---

### **Step 4: Enable Bedrock Model Access** (2 minutes)

**This is the most important step!**

1. In AWS Console, search for **"Bedrock"**
2. Click **"Amazon Bedrock"**
3. In left sidebar, click **"Model access"**
4. Click **"Manage model access"** (orange button)
5. Find **"Anthropic"** section
6. Check the box for:
   - ✅ **Claude 3.5 Sonnet v2** (or latest available)
   - ✅ **Claude 3 Sonnet** (backup)
7. Scroll down and click **"Request model access"**
8. Wait 2-5 minutes (usually instant)
9. Refresh page - status should show **"Access granted"** ✅

**Note**: If you see "Pending", wait a few minutes and refresh.

---

### **Step 5: Configure Your Application** (1 minute)

Create `.env` file in `backend/` directory:

```bash
# AWS Credentials
AWS_ACCESS_KEY_ID=AKIA...your-key-here
AWS_SECRET_ACCESS_KEY=wJalrXUtn...your-secret-here
AWS_REGION=us-east-1

# Optional - S3 bucket (can leave empty for mock mode)
S3_BUCKET_NAME=

# Optional - OpenSearch (can leave empty for mock mode)
OPENSEARCH_ENDPOINT=

# Debug Settings
DEBUG_MODE=true
TRACE_AGENTS=true
TRACE_LLM_CALLS=true
```

**Replace** `AKIA...` and `wJalrXUtn...` with your actual keys from Step 3.

---

### **Step 6: Test Your Setup** (1 minute)

```bash
# Test AWS credentials
aws configure list

# Test Bedrock access
aws bedrock list-foundation-models --region us-east-1

# Should show Claude models available
```

Or test in Python:

```python
import boto3

# Test connection
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
print("✅ AWS Bedrock connection successful!")
```

---

## 🎯 Quick Summary

**What you created:**
1. ✅ AWS Account
2. ✅ IAM User (`mediquery-dev`)
3. ✅ Access Keys (Access Key ID + Secret)
4. ✅ Bedrock Model Access (Claude Sonnet)

**What you DON'T need:**
- ❌ Anthropic API key
- ❌ Claude subscription
- ❌ Any other API keys

**Total time**: ~15 minutes
**Total cost**: $0 (free tier covers demo usage)

---

## 💰 Cost Breakdown

### **Free Tier** (First 12 months)
- S3: 5GB storage free
- Lambda: 1M requests/month free
- API Gateway: 1M calls/month free

### **Bedrock Pricing** (Pay-per-use)
**Claude Sonnet 4.6:**
- Input: ~$3 per 1M tokens
- Output: ~$15 per 1M tokens

**For your demo:**
- 50 queries × 500 tokens each = 25,000 tokens
- Cost: ~$0.10 - $0.50 total

**You'll spend less than $1 for the entire demo!**

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
# Create new key
aws iam create-access-key --user-name mediquery-dev

# Delete old key
aws iam delete-access-key --access-key-id AKIA... --user-name mediquery-dev
```

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
1. Go to Bedrock Console
2. Check "Model access" tab
3. Ensure Claude models show "Access granted"
4. Wait 5 minutes if status is "Pending"

### **Error: "Region not supported"**

**Solution**: Use supported region

```bash
# Bedrock is available in:
us-east-1  # ✅ Recommended (N. Virginia)
us-west-2  # Oregon
eu-central-1  # Frankfurt
```

Change in `.env`:
```bash
AWS_REGION=us-east-1
```

---

## ✅ Verification Checklist

Before running your app:

- [ ] AWS account created
- [ ] IAM user created (`mediquery-dev`)
- [ ] Access keys downloaded
- [ ] Bedrock model access enabled (Claude Sonnet)
- [ ] `.env` file created with credentials
- [ ] Credentials tested (optional)

---

## 🚀 You're Ready!

**Start your application:**

```bash
# Backend
cd backend
python3 -m uvicorn app.main:app --reload

# Frontend
cd frontend
npm run dev
```

**Upload a PDF and start querying!** 🎉

---

## 📞 Need Help?

**AWS Support:**
- Free tier support: https://aws.amazon.com/premiumsupport/
- Bedrock docs: https://docs.aws.amazon.com/bedrock/
- IAM docs: https://docs.aws.amazon.com/iam/

**Common Issues:**
- Bedrock not available in region → Use `us-east-1`
- Model access pending → Wait 5 minutes
- Credentials not working → Recreate access keys

---

**Remember**: You only need AWS credentials. No separate Claude API key needed!
