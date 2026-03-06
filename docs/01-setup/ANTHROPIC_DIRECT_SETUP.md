# Anthropic Direct API Setup (Temporary Fallback)

## ⚠️ SECURITY WARNING

**This configuration bypasses AWS Bedrock security guarantees.**

Using Anthropic's API directly means:
- ❌ Data is sent directly to Anthropic's servers
- ❌ No AWS Bedrock data isolation/privacy
- ❌ Anthropic may retain conversation data per their policies
- ❌ Does not meet original security requirements

**Use ONLY as temporary fallback while AWS Marketplace subscription is pending.**

---

## 🔧 Setup Instructions

### 1. Get Anthropic API Key

1. Go to: https://console.anthropic.com/
2. Sign up or log in
3. Navigate to **API Keys**
4. Click **"Create Key"**
5. Copy the API key (starts with `sk-ant-`)

### 2. Update `.env` File

```bash
# Enable direct Anthropic API
USE_DIRECT_ANTHROPIC=true

# Add your Anthropic API key
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Model to use (default is Claude 3.5 Sonnet)
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

### 3. Restart Backend

```bash
# Kill existing backend
lsof -ti:8000 | xargs kill -9

# Start backend
cd backend && python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Verify It's Working

Check backend logs for:
```
⚠️  Initializing DIRECT Anthropic API (bypassing Bedrock security)
✅ Claude direct API service initialized
```

Test query:
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "what is this document about", "document_id": "doc_d7b624a0f035"}'
```

You should see a real answer instead of error message.

---

## 🔄 Switch Back to Bedrock

Once AWS Marketplace subscription is approved:

### 1. Update `.env`

```bash
# Disable direct Anthropic API
USE_DIRECT_ANTHROPIC=false

# Keep Bedrock configuration
BEDROCK_MODEL_ID=us.anthropic.claude-haiku-4-5-20251001-v1:0
```

### 2. Restart Backend

The system will automatically use Bedrock again.

### 3. Verify Bedrock Working

```bash
python3 test_bedrock_access.py
```

Should show: `✅ SUCCESS! Model is accessible`

---

## 📊 How It Works

### Architecture

```
Query Request
    ↓
Synthesis Agent
    ↓
Check: USE_DIRECT_ANTHROPIC flag
    ↓
├─ TRUE  → claude.py (Direct Anthropic API)
└─ FALSE → bedrock.py (AWS Bedrock)
    ↓
Generate Answer
```

### Code Changes

1. **`backend/app/config.py`**
   - Added `use_direct_anthropic` flag
   - Added `anthropic_api_key` setting
   - Added `anthropic_model` setting

2. **`backend/app/services/claude.py`** (NEW)
   - Direct Anthropic API client
   - Same interface as `bedrock.py`
   - Includes security warnings in logs

3. **`backend/app/agents/synthesis.py`**
   - Checks `use_direct_anthropic` flag
   - Routes to appropriate service
   - Logs which service is being used

4. **`backend/.env`**
   - Added configuration flags
   - Added API key placeholder

### No Changes to:
- ✅ `bedrock.py` - Unchanged, ready for production
- ✅ Other agents - No modifications needed
- ✅ API endpoints - Same interface
- ✅ Frontend - No changes required

---

## 💰 Pricing

### Anthropic Direct API
- Claude 3.5 Sonnet: $3 per million input tokens, $15 per million output tokens
- Claude 3 Haiku: $0.25 per million input tokens, $1.25 per million output tokens

### AWS Bedrock (When Available)
- Same models, similar pricing
- Plus AWS infrastructure costs
- But with enterprise security guarantees

---

## 🧪 Testing

### Test Direct Anthropic API

```python
# Test script
python3 -c "
from anthropic import Anthropic

client = Anthropic(api_key='your-key-here')
message = client.messages.create(
    model='claude-3-5-sonnet-20241022',
    max_tokens=100,
    messages=[{'role': 'user', 'content': 'Say hello'}]
)
print(message.content[0].text)
"
```

### Test Full Flow

1. Upload a document via frontend
2. Ask a question
3. Check backend logs for: `⚠️  Using DIRECT Anthropic API`
4. Verify answer is generated correctly

---

## 📝 Cleanup After AWS Resolution

Once AWS Bedrock Marketplace subscription is approved:

1. Set `USE_DIRECT_ANTHROPIC=false` in `.env`
2. Restart backend
3. Test with Bedrock
4. (Optional) Remove `anthropic` package: `pip3 uninstall anthropic`
5. (Optional) Delete `backend/app/services/claude.py`
6. (Optional) Remove Anthropic config from `config.py`

---

## 🔒 Security Reminder

**This is a TEMPORARY solution.**

For production deployment:
- ✅ Use AWS Bedrock only
- ✅ Enable all Bedrock security features
- ✅ Remove direct Anthropic API code
- ✅ Document security compliance

**Do not deploy to production with `USE_DIRECT_ANTHROPIC=true`**
