# ChromaDB Vector Database Setup

## 🎯 **Overview**

ChromaDB is now integrated as an **alternative vector database** for the RAG system, replacing OpenSearch when it's not available. This enables **real vector storage and retrieval** for testing and development.

---

## 🔧 **Architecture**

### **Flag-Based Routing (Similar to Anthropic Direct API)**

```
Document Upload
    ↓
Check: USE_CHROMADB flag
    ↓
├─ TRUE  → ChromaDB (Local persistent storage)
└─ FALSE → OpenSearch (AWS managed service)
    ↓
Store embeddings + metadata
```

### **RAG Flow with ChromaDB**

```
1. PDF Upload
   ├─ Extract text from PDF
   ├─ Chunk text (500 chars with 50 char overlap)
   ├─ Generate embeddings (BAAI/bge-large-en-v1.5)
   └─ Store in ChromaDB collection

2. User Query
   ├─ Generate query embedding
   ├─ Vector search in ChromaDB (cosine similarity)
   ├─ Retrieve top-k relevant chunks
   └─ Pass to LLM for answer generation

3. Document Summary
   ├─ Retrieve all chunks from ChromaDB
   ├─ Combine text
   └─ Generate summary with LLM
```

---

## 📁 **Files Created/Modified**

### **New Files:**
- `backend/app/services/chromadb_service.py` - ChromaDB service implementation

### **Modified Files:**
- `backend/app/config.py` - Added USE_CHROMADB flag
- `backend/app/api/upload.py` - Routes to ChromaDB or OpenSearch
- `backend/app/agents/retrieval.py` - Uses ChromaDB for vector search
- `backend/app/api/documents.py` - Uses ChromaDB for summary/list
- `backend/.env` - Added ChromaDB configuration

---

## ⚙️ **Configuration**

### **Environment Variables (.env)**

```bash
# ChromaDB (Alternative vector database for testing)
USE_CHROMADB=true
CHROMADB_PERSIST_DIRECTORY=./chroma_data
```

### **When to Use ChromaDB vs OpenSearch**

| Scenario | Use ChromaDB | Use OpenSearch |
|----------|--------------|----------------|
| Local development | ✅ | ❌ |
| Testing RAG without AWS | ✅ | ❌ |
| Production deployment | ❌ | ✅ |
| AWS infrastructure available | ❌ | ✅ |
| Quick prototyping | ✅ | ❌ |

---

## 🚀 **Usage**

### **1. Enable ChromaDB**

Update `backend/.env`:
```bash
USE_CHROMADB=true
```

### **2. Restart Backend**

```bash
cd backend
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### **3. Upload a Document**

The system will automatically:
- Extract text from PDF
- Generate embeddings
- Store in ChromaDB collection (one per document)
- Create persistent storage in `./chroma_data/`

### **4. Query the Document**

Ask questions - the system will:
- Generate query embedding
- Search ChromaDB for similar chunks
- Return top-k results to LLM
- Generate answer with citations

---

## 📊 **ChromaDB Features**

### **What ChromaDB Provides:**

✅ **Persistent Storage** - Data saved to disk, survives restarts  
✅ **Cosine Similarity** - Accurate vector search  
✅ **Metadata Filtering** - Filter by document_id, page, etc.  
✅ **Collection Management** - One collection per document  
✅ **No External Dependencies** - Runs locally, no cloud setup  
✅ **Fast Queries** - Optimized for similarity search  

### **ChromaDB vs OpenSearch:**

| Feature | ChromaDB | OpenSearch |
|---------|----------|------------|
| Setup | Zero config | Requires AWS setup |
| Cost | Free | AWS charges |
| Hybrid Search | Vector only | Vector + keyword |
| Scale | Single machine | Distributed cluster |
| Production | Not recommended | Production-ready |
| Development | Perfect | Overkill |

---

## 🔍 **How It Works**

### **1. Document Indexing (upload.py)**

```python
if settings.use_chromadb:
    chromadb_svc = get_chromadb_service()
    collection_name = f"medical-docs-{document_id}"
    
    for chunk in text_chunks:
        embedding = await embedding_service.encode_single(chunk['text'])
        
        chromadb_svc.index_document(
            collection_name=collection_name,
            doc_id=f"{document_id}_{chunk['chunk_id']}",
            text=chunk['text'],
            embedding=embedding,
            metadata={'document_id': document_id, 'page': chunk['page']}
        )
```

### **2. Vector Search (retrieval.py)**

```python
if settings.use_chromadb:
    chromadb_svc = get_chromadb_service()
    
    chunks = await chromadb_svc.vector_search(
        collection_name=f"medical-docs-{document_id}",
        query_embedding=query_embedding,
        top_k=10
    )
    # Returns: [{'text': '...', 'metadata': {...}, 'score': 0.95}, ...]
```

### **3. Collection Structure**

Each document gets its own collection:
```
chroma_data/
├── medical-docs-doc_abc123/
│   ├── chunk_0_0 (text + embedding + metadata)
│   ├── chunk_0_500 (text + embedding + metadata)
│   └── chunk_1_0 (text + embedding + metadata)
└── medical-docs-doc_xyz789/
    └── ...
```

---

## 🧪 **Testing**

### **Test 1: Upload a Document**

```bash
curl -X POST http://localhost:8000/api/v1/upload \
  -F "file=@test.pdf" \
  -F "title=Test Medical Report"
```

**Expected logs:**
```
📊 Using ChromaDB for vector storage
✅ Document indexed (collection: medical-docs-doc_xxx)
```

### **Test 2: Query the Document**

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "what are the blood glucose levels", "document_id": "doc_xxx"}'
```

**Expected logs:**
```
📊 Using ChromaDB for retrieval
✅ Vector search complete (results: 10, top_score: 0.92)
```

### **Test 3: Verify Data Persistence**

```bash
# Check ChromaDB data directory
ls -la ./chroma_data/
```

You should see SQLite database files with your collections.

---

## 🔄 **Switch Back to OpenSearch**

When OpenSearch is available:

### **1. Update .env**

```bash
USE_CHROMADB=false
OPENSEARCH_ENDPOINT=https://your-domain.us-east-1.es.amazonaws.com
```

### **2. Restart Backend**

The system automatically routes to OpenSearch.

---

## 📝 **Implementation Details**

### **ChromaDB Service (chromadb_service.py)**

**Key Methods:**

1. `index_document()` - Store chunk with embedding
2. `vector_search()` - Cosine similarity search
3. `hybrid_search()` - Alias for vector_search (ChromaDB doesn't have true hybrid)
4. `get_or_create_collection()` - Collection management
5. `delete_collection()` - Cleanup

**Similarity Scoring:**
```python
# ChromaDB returns distance, convert to similarity
distance = results['distances'][0][i]
score = 1 - distance  # Cosine similarity (0-1 range)
```

### **Collection Naming Convention**

```
medical-docs-{document_id}
```

Each document gets a unique collection for isolation and easy deletion.

---

## ⚠️ **Limitations**

1. **No True Hybrid Search** - ChromaDB only does vector search (no keyword BM25)
2. **Single Machine** - Not distributed like OpenSearch
3. **Limited Scale** - Best for <1M vectors
4. **No Advanced Features** - No aggregations, complex filters, etc.

**For Production:** Use OpenSearch  
**For Development/Testing:** ChromaDB is perfect

---

## 🎯 **Current Status**

✅ **ChromaDB installed and configured**  
✅ **Flag-based routing implemented**  
✅ **Upload endpoint routes to ChromaDB**  
✅ **Retrieval agent uses ChromaDB**  
✅ **Document summary uses ChromaDB**  
✅ **Persistent storage enabled**  

**Ready to test full RAG flow with real vector storage!**

---

## 🔐 **Security Note**

ChromaDB stores data locally in `./chroma_data/`. This directory contains:
- Vector embeddings
- Document chunks
- Metadata

**For production:**
- Use OpenSearch with proper AWS security
- Enable encryption at rest
- Implement access controls
- Use VPC endpoints

**ChromaDB is for development/testing only.**
