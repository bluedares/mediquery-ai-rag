# GitHub Repository Setup Guide

## 🎯 **Recommended Repository Details**

### **Repository Name:**
```
mediquery-ai-rag
```

### **Description:**
```
🏥 Medical Document RAG System - AI-powered medical report analysis using Claude, ChromaDB, and React. Ask questions about your health reports in plain language.
```

### **Tags/Topics:**
```
rag, medical-ai, healthcare, claude, chromadb, fastapi, react, vector-database, llm, medical-reports, document-analysis, ai-assistant
```

### **Visibility:**
- **Public** ✅ (Recommended for portfolio/demo)
- Private ❌ (Use if contains sensitive data)

---

## 🔒 **Security Checklist (CRITICAL)**

Before pushing to GitHub, verify these files are **NOT** committed:

✅ **Protected by .gitignore:**
- ✅ `backend/.env` - Contains API keys
- ✅ `chroma_data/` - Local vector database
- ✅ `.aws/` - AWS credentials
- ✅ `*.pem`, `*.key` - Private keys
- ✅ `test_documents/*.pdf` - Test medical documents
- ✅ `node_modules/` - Dependencies

⚠️ **Files to Review Before Commit:**
- `README.md` - Remove any sensitive info
- `backend/app/config.py` - Ensure no hardcoded keys
- Any documentation with API keys or credentials

---

## 📝 **Step-by-Step GitHub Setup**

### **Step 1: Create GitHub Repository**

1. Go to: https://github.com/new
2. Fill in details:
   - **Repository name:** `mediquery-ai-rag`
   - **Description:** `🏥 Medical Document RAG System - AI-powered medical report analysis using Claude, ChromaDB, and React`
   - **Visibility:** Public ✅
   - **Initialize:** 
     - ❌ Do NOT add README (we have one)
     - ❌ Do NOT add .gitignore (we have one)
     - ❌ Do NOT add license (add later if needed)
3. Click **"Create repository"**

---

### **Step 2: Initialize Local Git Repository**

```bash
cd /Volumes/WorkSpace/Projects/InterviewPreps/IndegeneProject

# Initialize git
git init

# Verify .gitignore is working
git status

# Should NOT see:
# - backend/.env
# - chroma_data/
# - node_modules/
# - test_documents/*.pdf
```

---

### **Step 3: Create Initial Commit**

```bash
# Add all files (respecting .gitignore)
git add .

# Verify what will be committed
git status

# Create initial commit
git commit -m "Initial commit: MediQuery AI RAG System

- FastAPI backend with Claude LLM integration
- React frontend with chat interface
- ChromaDB vector database for RAG
- AWS Bedrock support (with Anthropic fallback)
- Document upload and processing
- Health metrics extraction
- Complete documentation structure"
```

---

### **Step 4: Connect to GitHub**

```bash
# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/mediquery-ai-rag.git

# Verify remote
git remote -v
```

---

### **Step 5: Push to GitHub**

```bash
# Push to main branch
git branch -M main
git push -u origin main
```

---

## 🔍 **Verify Security After Push**

1. Go to your GitHub repository
2. Check these files are **NOT** visible:
   - ❌ `backend/.env`
   - ❌ `chroma_data/`
   - ❌ Any API keys or credentials
3. If you see sensitive files:
   ```bash
   # Remove from git history
   git rm --cached backend/.env
   git commit -m "Remove sensitive files"
   git push
   ```

---

## 📄 **Recommended README.md Updates**

Add to your README.md:

```markdown
## 🔐 Environment Setup

1. Copy environment template:
   ```bash
   cp backend/.env.example backend/.env
   ```

2. Add your credentials:
   ```
   AWS_ACCESS_KEY_ID=your_key_here
   AWS_SECRET_ACCESS_KEY=your_secret_here
   ANTHROPIC_API_KEY=your_anthropic_key_here
   ```

⚠️ **Never commit .env files to version control**
```

---

## 🎨 **Optional: Add GitHub Repository Badges**

Add to top of README.md:

```markdown
# MediQuery AI

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
```

---

## 🚀 **Post-Push Checklist**

After pushing to GitHub:

✅ Repository is accessible  
✅ No sensitive files visible  
✅ README.md displays correctly  
✅ Documentation is organized  
✅ .gitignore is working  
✅ All code is present  
✅ No API keys in code  

---

## 🔄 **Future Updates**

To push changes:

```bash
# Check status
git status

# Add changes
git add .

# Commit with message
git commit -m "Your commit message"

# Push to GitHub
git push
```

---

## ⚠️ **If You Accidentally Commit Sensitive Data**

**Immediate Actions:**

1. **Rotate all exposed credentials:**
   - AWS keys
   - Anthropic API keys
   - Any other secrets

2. **Remove from git history:**
   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch backend/.env" \
     --prune-empty --tag-name-filter cat -- --all
   
   git push origin --force --all
   ```

3. **Add to .gitignore and commit:**
   ```bash
   echo "backend/.env" >> .gitignore
   git add .gitignore
   git commit -m "Add .env to gitignore"
   git push
   ```

---

## 📞 **Need Help?**

- GitHub Docs: https://docs.github.com/
- Git Basics: https://git-scm.com/book/en/v2
- Remove Sensitive Data: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository

---

**Remember: NEVER commit API keys, credentials, or sensitive data to GitHub!** 🔒
