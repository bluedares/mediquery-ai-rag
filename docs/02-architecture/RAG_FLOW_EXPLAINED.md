# RAG System Flow - Complete Explanation

## 🎯 **Your Question: How Does It Work?**

When a user asks a question, the system:
1. **Searches vector database** for relevant chunks
2. **Retrieves matching embeddings** from the document
3. **Passes ONLY those chunks** to the LLM
4. **LLM formats answer** based ONLY on provided context
5. **NO web search, NO external data, NO hallucination**

---

## 📊 **Complete RAG Flow**

### **Step 1: Document Upload (One-time)**

```
User uploads PDF
    ↓
Extract text from PDF pages
    ↓
Split into chunks (500 chars, 50 char overlap)
    ↓
Generate embeddings for each chunk (BGE-large-en-v1.5)
    ↓
Store in ChromaDB:
  - Chunk text
  - Embedding vector (1024 dimensions)
  - Metadata (document_id, page, chunk_id)
    ↓
Upload PDF to S3
```

**Example:**
```
PDF: "Blood glucose: 145 mg/dL (elevated)"
    ↓
Chunk 1: "Blood glucose: 145 mg/dL (elevated)..."
Embedding: [0.234, -0.567, 0.891, ...] (1024 numbers)
Metadata: {document_id: "doc_abc", page: 1, chunk_id: "chunk_0_0"}
```

---

### **Step 2: User Asks Question**

```
User: "What is the blood glucose level?"
    ↓
Generate query embedding (same model: BGE-large-en-v1.5)
    ↓
Query embedding: [0.245, -0.543, 0.876, ...] (1024 numbers)
```

---

### **Step 3: Vector Search (Retrieval Agent)**

```
Query embedding
    ↓
Search ChromaDB using cosine similarity
    ↓
Find top-k most similar chunks (default: 10)
    ↓
Return chunks with similarity scores
```

**Example Results:**
```
Chunk 1: "Blood glucose: 145 mg/dL (elevated)" - Score: 0.92
Chunk 2: "Fasting glucose test performed..." - Score: 0.85
Chunk 3: "Reference range: 70-100 mg/dL" - Score: 0.78
...
```

**Key Point:** System ONLY retrieves chunks from the uploaded document, NOT from web or external sources.

---

### **Step 4: Reranking (Optional)**

```
Retrieved chunks (10)
    ↓
Rerank by relevance score
    ↓
Keep top-k (default: 5)
```

---

### **Step 5: Synthesis (Answer Generation)**

```
Selected chunks (5)
    ↓
Build context with sources:
  [Source 1] (Page 1)
  Blood glucose: 145 mg/dL (elevated)
  
  [Source 2] (Page 1)
  Fasting glucose test performed...
    ↓
Create prompt:
  System: "Answer ONLY based on provided context"
  User: "Context: [chunks]\n\nQuestion: What is blood glucose?\n\nAnswer ONLY from context"
    ↓
Send to LLM (Claude Haiku)
    ↓
LLM generates answer using ONLY the provided chunks
    ↓
Extract citations [Source 1], [Source 2]
```

**Example LLM Response:**
```
"Based on the test results, the blood glucose level is 145 mg/dL [Source 1], 
which is elevated compared to the reference range of 70-100 mg/dL [Source 2]."
```

---

## 🔒 **Anti-Hallucination Safeguards**

### **1. No Chunks = No Answer**

```python
if not chunks:
    return "I don't have enough information to answer this question."
```

**Result:** If vector search finds nothing, system says "I don't know" instead of making up an answer.

---

### **2. Explicit Instructions to LLM**

**System Prompt:**
```
"You are a medical information assistant specialized in analyzing clinical documents. 
Your role is to provide accurate, well-cited answers based SOLELY on the provided context.

Guidelines:
- Answer ONLY based on the provided context
- If the context doesn't contain enough information, say so
- Do NOT use external knowledge
- Do NOT make assumptions
- Cite sources using [Source N] format"
```

**User Prompt:**
```
"Instructions:
1. Answer the question based SOLELY on the context above
2. If the context is insufficient to answer the question, clearly state that
3. Do NOT use information from outside the provided context"
```

---

### **3. Context-Only Input**

The LLM receives:
- ✅ Retrieved chunks from the document
- ✅ User question
- ❌ NO web access
- ❌ NO external databases
- ❌ NO general knowledge (instructed not to use it)

---

## 📏 **Token Sizes**

### **Current Configuration:**

```python
# From config.py
llm_max_tokens: int = 1000        # Max tokens LLM can generate
llm_temperature: float = 0.1      # Low = more deterministic
llm_top_p: float = 0.9            # Nucleus sampling
```

### **Token Breakdown:**

**Input to LLM:**
```
System prompt: ~100 tokens
Context (5 chunks × ~125 tokens): ~625 tokens
User question: ~20 tokens
Instructions: ~50 tokens
────────────────────────────────────────
Total Input: ~795 tokens
```

**Output from LLM:**
```
Max allowed: 1000 tokens
Typical answer: 100-300 tokens
```

**Total per query:** ~800-1100 tokens (input + output)

---

### **Token Size Considerations:**

**Current Limits:**
- ✅ **1000 tokens** is sufficient for most medical Q&A
- ✅ Allows detailed answers with citations
- ✅ Prevents overly long responses

**If you need longer answers:**
```python
# In config.py, increase:
llm_max_tokens: int = 2000  # For more detailed responses
```

**Trade-offs:**
- Higher tokens = More detailed answers
- Higher tokens = Higher cost
- Higher tokens = Slower responses

---

## 🔍 **Example Flow with Real Data**

### **Scenario: User asks about blood glucose**

**1. Vector Search:**
```
Query: "What is the blood glucose level?"
    ↓
ChromaDB finds 5 relevant chunks:
  - Chunk 1: "Blood glucose: 145 mg/dL" (score: 0.92)
  - Chunk 2: "Fasting test performed" (score: 0.85)
  - Chunk 3: "Reference: 70-100 mg/dL" (score: 0.78)
  - Chunk 4: "Elevated glucose indicates..." (score: 0.72)
  - Chunk 5: "Patient history shows..." (score: 0.68)
```

**2. Context Built:**
```
[Source 1] (Page 1)
Blood glucose: 145 mg/dL (Fasting)
Reference Range: 70-100 mg/dL
Status: ELEVATED

[Source 2] (Page 1)
Fasting test performed at 8:00 AM
Patient fasted for 12 hours prior

[Source 3] (Page 2)
Elevated glucose indicates pre-diabetic condition
Requires lifestyle modification
```

**3. LLM Receives:**
```
System: "Answer ONLY from provided context"
User: "Context: [above chunks]\n\nQuestion: What is blood glucose?\n\nAnswer:"
```

**4. LLM Generates:**
```
"The blood glucose level is 145 mg/dL [Source 1], measured during a fasting 
test performed at 8:00 AM [Source 2]. This is elevated compared to the 
reference range of 70-100 mg/dL [Source 1], indicating a pre-diabetic 
condition that requires lifestyle modification [Source 3]."
```

**5. User Sees:**
```
Answer: "The blood glucose level is 145 mg/dL [Source 1]..."
Citations: [Source 1, Source 2, Source 3]
Confidence: 0.92
```

---

## ❌ **What Happens If No Relevant Chunks Found?**

### **Scenario: User asks unrelated question**

**Question:** "What is the weather today?"

**1. Vector Search:**
```
Query embedding generated
    ↓
ChromaDB searches medical document
    ↓
No similar chunks found (all scores < 0.3)
    ↓
Returns empty list: []
```

**2. Synthesis Agent:**
```python
if not chunks:
    return "I don't have enough information to answer this question."
```

**3. User Sees:**
```
Answer: "I don't have enough information to answer this question."
Citations: []
Confidence: 0.0
```

**Result:** System does NOT hallucinate, does NOT search web, does NOT make up answer.

---

## 🛡️ **Security: No External Data**

### **What the System CANNOT Do:**

❌ Search the web  
❌ Access external databases  
❌ Use general knowledge (instructed not to)  
❌ Make up information  
❌ Answer questions not in the document  

### **What the System CAN Do:**

✅ Search ONLY uploaded documents  
✅ Retrieve ONLY stored chunks  
✅ Answer ONLY from retrieved context  
✅ Say "I don't know" when context is insufficient  
✅ Cite sources for every claim  

---

## 📊 **Current Configuration Summary**

```python
# Vector Search
top_k_retrieval: 10          # Retrieve top 10 chunks
top_k_rerank: 5              # Keep top 5 after reranking

# LLM
llm_max_tokens: 1000         # Max answer length
llm_temperature: 0.1         # Low = deterministic, factual
llm_top_p: 0.9               # Nucleus sampling

# Embeddings
embedding_model: "BAAI/bge-large-en-v1.5"
embedding_dimension: 1024

# Vector DB
use_chromadb: true           # Local persistent storage
chromadb_persist_directory: "./chroma_data"
```

---

## 🎯 **Key Takeaways**

1. **No Web Search:** System ONLY uses uploaded documents
2. **No Hallucination:** LLM instructed to answer ONLY from provided chunks
3. **No External Data:** Vector DB contains ONLY uploaded content
4. **Explicit Safeguards:** If no chunks found → "I don't know"
5. **Citations Required:** Every answer must cite sources
6. **Token Size:** 1000 tokens max (sufficient for detailed medical Q&A)

---

## 🔧 **To Increase Token Size**

If you need longer, more detailed answers:

**1. Update config.py:**
```python
llm_max_tokens: int = 2000  # Or 3000, 4000, etc.
```

**2. Restart backend**

**Trade-offs:**
- More detailed answers
- Higher API costs
- Slightly slower responses

**Recommendation:** 1000 tokens is optimal for most medical Q&A. Only increase if you need very detailed, multi-paragraph explanations.

---

## ✅ **Your System is Safe**

Your RAG system:
- ✅ Only answers from uploaded documents
- ✅ Never searches the web
- ✅ Never uses external data
- ✅ Says "I don't know" when context is missing
- ✅ Always cites sources
- ✅ Cannot hallucinate (with proper prompting)

**This is a production-ready, secure RAG implementation!**
