# 📄 PDF Upload Flow - Internal Processing

## 🎯 Overview

When a user uploads a PDF, the system processes it through multiple stages involving text extraction, chunking, embedding generation, and indexing for semantic search.

---

## 🔄 Complete Flow Diagram

```
User Upload PDF
      ↓
[1] Frontend: File Selection
      ↓
[2] Frontend: Progress UI (Uploading → Tokenizing → Embedding → Analyzing)
      ↓
[3] Backend: Receive PDF File
      ↓
[4] Backend: Validate PDF
      ↓
[5] Backend: Extract Text (PyPDF2)
      ↓
[6] Backend: Chunk Text
      ↓
[7] Backend: Generate Embeddings
      ↓
[8] Backend: Upload to S3
      ↓
[9] Backend: Index in OpenSearch
      ↓
[10] Backend: Return Document ID
      ↓
[11] Frontend: Show Summary
      ↓
[12] Frontend: Enable Query Interface
```

---

## 📋 Detailed Step-by-Step Process

### **Step 1: User Selects PDF File**
**Location**: `frontend/src/App.jsx` → `handleUpload()`

```javascript
const handleUpload = async (e) => {
  const file = e.target.files[0]  // Get selected PDF
  const formData = new FormData()
  formData.append('file', file)
  
  // Show progress: "Uploading"
  setUploadProgress('uploading')
}
```

**What happens:**
- User clicks "Choose PDF File" button
- Browser file picker opens
- User selects a PDF file
- FormData object created with the file

---

### **Step 2: Frontend Progress Stages**
**Location**: `frontend/src/App.jsx`

```javascript
// Simulate progress stages for UX
setTimeout(() => setUploadProgress('tokenizing'), 500)
setTimeout(() => setUploadProgress('embedding'), 1500)
setTimeout(() => setUploadProgress('analyzing'), 3000)
```

**Progress Stages Shown:**
1. ⏳ **Uploading PDF** - File being sent to backend
2. ⏳ **Creating Tokens** - Text being split into chunks
3. ⏳ **Creating Embeddings** - Generating vector representations
4. ⏳ **Analyzing Document** - Indexing and finalizing
5. ✅ **Ready!** - Document processed successfully

---

### **Step 3: Backend Receives PDF**
**Location**: `backend/app/api/upload.py` → `upload_document()`

```python
@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
):
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(400, "Only PDF files allowed")
    
    # Read file content
    content = await file.read()
```

**What happens:**
- FastAPI endpoint receives multipart/form-data
- File validation (PDF only)
- File content read into memory

---

### **Step 4: PDF Validation**
**Location**: `backend/app/api/upload.py`

```python
# Check file size
if len(content) > settings.max_file_size:
    raise HTTPException(400, "File too large")

# Validate PDF format
try:
    pdf_reader = PdfReader(io.BytesIO(content))
except Exception:
    raise HTTPException(400, "Invalid PDF file")
```

**Checks:**
- File size < 50MB
- Valid PDF format
- Readable by PyPDF2

---

### **Step 5: Text Extraction**
**Location**: `backend/app/api/upload.py`

```python
from PyPDF2 import PdfReader

# Extract text from all pages
pdf_reader = PdfReader(io.BytesIO(content))
full_text = ""
page_count = len(pdf_reader.pages)

for page_num, page in enumerate(pdf_reader.pages):
    text = page.extract_text()
    full_text += f"\n--- Page {page_num + 1} ---\n{text}"
```

**What happens:**
- PyPDF2 reads PDF structure
- Extracts text from each page
- Preserves page numbers for citations
- Combines into single text document

**Example Output:**
```
--- Page 1 ---
Phase III Clinical Trial Protocol
Drug X for Treatment of Hypertension
...

--- Page 2 ---
Primary Endpoint
Reduction in systolic blood pressure...
```

---

### **Step 6: Text Chunking**
**Location**: `backend/app/api/upload.py`

```python
# Split text into chunks
chunk_size = 500  # characters
chunk_overlap = 50  # characters

chunks = []
for i in range(0, len(full_text), chunk_size - chunk_overlap):
    chunk = full_text[i:i + chunk_size]
    chunks.append({
        'text': chunk,
        'page': extract_page_number(chunk),
        'chunk_id': i // (chunk_size - chunk_overlap)
    })
```

**Why Chunking?**
- LLMs have token limits
- Better semantic search granularity
- Enables precise citations

**Chunk Strategy:**
- **Size**: 500 characters (~125 tokens)
- **Overlap**: 50 characters (prevents context loss at boundaries)
- **Metadata**: Page number, chunk ID

**Example Chunks:**
```
Chunk 0: "Phase III Clinical Trial Protocol Drug X for..."
Chunk 1: "...Drug X for Treatment of Hypertension. Study..."
Chunk 2: "...Study Duration: 12 weeks. Primary Endpoint..."
```

---

### **Step 7: Generate Embeddings**
**Location**: `backend/app/services/embeddings.py`

```python
from sentence_transformers import SentenceTransformer

# Load embedding model
model = SentenceTransformer('BAAI/bge-large-en-v1.5')

# Generate embeddings for all chunks
embeddings = []
for chunk in chunks:
    # Convert text to 1024-dimensional vector
    embedding = model.encode(chunk['text'])
    embeddings.append({
        'chunk_id': chunk['chunk_id'],
        'text': chunk['text'],
        'vector': embedding.tolist(),  # [0.123, -0.456, ...]
        'page': chunk['page']
    })
```

**What are Embeddings?**
- Vector representations of text (1024 dimensions)
- Semantically similar text → similar vectors
- Enables semantic search (not just keyword matching)

**Example:**
```
Text: "Primary endpoint is blood pressure reduction"
Vector: [0.123, -0.456, 0.789, ..., 0.234]  (1024 numbers)

Text: "Main goal is lowering BP"
Vector: [0.119, -0.461, 0.792, ..., 0.229]  (similar!)
```

---

### **Step 8: Upload to S3**
**Location**: `backend/app/services/s3.py`

```python
import boto3

s3_client = boto3.client('s3',
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
    region_name=settings.aws_region
)

# Upload original PDF
document_id = f"doc_{uuid.uuid4().hex[:12]}"
s3_key = f"documents/{document_id}.pdf"

s3_client.put_object(
    Bucket=settings.s3_bucket,
    Key=s3_key,
    Body=content,
    ContentType='application/pdf'
)
```

**What happens:**
- Generate unique document ID
- Upload PDF to S3 bucket
- Store for future reference/download

**S3 Structure:**
```
mediquery-documents/
  └── documents/
      ├── doc_abc123def456.pdf
      ├── doc_xyz789ghi012.pdf
      └── ...
```

---

### **Step 9: Index in OpenSearch**
**Location**: `backend/app/services/opensearch.py`

```python
from opensearchpy import OpenSearch

# Connect to OpenSearch
client = OpenSearch(
    hosts=[settings.opensearch_endpoint],
    use_ssl=True
)

# Index each chunk with embedding
for embedding in embeddings:
    client.index(
        index='medical-documents',
        body={
            'document_id': document_id,
            'chunk_id': embedding['chunk_id'],
            'text': embedding['text'],
            'embedding': embedding['vector'],
            'page': embedding['page'],
            'timestamp': datetime.now()
        }
    )
```

**What is OpenSearch?**
- Vector database for semantic search
- Stores text + embeddings
- Enables k-NN (nearest neighbor) search

**Index Structure:**
```json
{
  "document_id": "doc_abc123def456",
  "chunk_id": 0,
  "text": "Phase III Clinical Trial...",
  "embedding": [0.123, -0.456, ...],
  "page": 1,
  "timestamp": "2026-03-05T17:00:00Z"
}
```

---

### **Step 10: Return Document Metadata**
**Location**: `backend/app/api/upload.py`

```python
return {
    "document_id": document_id,
    "filename": file.filename,
    "pages": page_count,
    "chunks": len(chunks),
    "status": "success"
}
```

**Response Example:**
```json
{
  "document_id": "doc_abc123def456",
  "filename": "clinical_trial_hypertension.pdf",
  "pages": 2,
  "chunks": 15,
  "status": "success"
}
```

---

### **Step 11: Frontend Shows Summary**
**Location**: `frontend/src/App.jsx`

```javascript
// Generate summary
const summary = {
  title: response.data.filename.replace('.pdf', ''),
  pages: response.data.pages,
  chunks: response.data.chunks,
  keyPoints: [
    `Document contains ${response.data.pages} pages`,
    `Processed into ${response.data.chunks} searchable chunks`,
    `Embeddings created for semantic search`,
    `Ready for intelligent Q&A with Claude Sonnet 4.5`
  ]
}

setDocSummary(summary)
setShowSummary(true)
```

**Summary Screen Shows:**
- ✅ Success message
- 📊 Document statistics (pages, chunks, processing time)
- 🔍 Key details about processing
- 🚀 "Start Asking Questions" button

---

### **Step 12: Enable Query Interface**
**Location**: `frontend/src/App.jsx`

```javascript
const handleProceedToQuery = () => {
  setShowSummary(false)  // Hide summary
  // Query interface now visible
}
```

**Query Interface Shows:**
- Document info card (green)
- Query input textarea
- Example questions
- Debug toggle
- Submit button

---

## 🤖 When User Asks a Question

### **Query Processing Flow:**

```
User Query: "What are the primary endpoints?"
      ↓
[1] Generate query embedding
      ↓
[2] Search OpenSearch (k-NN with query vector)
      ↓
[3] Retrieve top 20 relevant chunks
      ↓
[4] LangGraph Multi-Agent System:
      ├─ Query Understanding Agent
      ├─ Document Retrieval Agent
      ├─ Answer Generation Agent (Claude Sonnet 4.5)
      └─ Verification Agent
      ↓
[5] Return answer + citations + debug trace
```

---

## 🔍 Technical Details

### **Embedding Model: BAAI/bge-large-en-v1.5**
- **Type**: Sentence Transformer
- **Dimensions**: 1024
- **Max Sequence Length**: 512 tokens
- **Use Case**: Semantic search, retrieval

### **LLM: Claude Sonnet 4.5**
- **Provider**: AWS Bedrock
- **Model ID**: `anthropic.claude-sonnet-4-5-20250514-v1:0`
- **Context Window**: 200K tokens
- **Use Case**: Answer generation, reasoning

### **Storage:**
- **S3**: Original PDFs
- **OpenSearch**: Chunks + embeddings for search
- **In-Memory**: Temporary processing

---

## 📊 Performance Metrics

**Typical Upload Processing:**
- PDF Upload: ~1 second
- Text Extraction: ~0.5 seconds
- Chunking: ~0.1 seconds
- Embedding Generation: ~2-3 seconds (15 chunks)
- S3 Upload: ~0.5 seconds
- OpenSearch Indexing: ~1 second

**Total**: ~5-6 seconds for a 2-page PDF

---

## 🎯 Key Takeaways

1. **Text Extraction**: PyPDF2 extracts raw text from PDF
2. **Chunking**: Splits text into 500-char chunks with 50-char overlap
3. **Embeddings**: Converts chunks to 1024-dim vectors for semantic search
4. **Storage**: PDF in S3, chunks+embeddings in OpenSearch
5. **Search**: Query embedding → k-NN search → retrieve relevant chunks
6. **Answer**: Claude Sonnet 4.5 generates answer from retrieved chunks

---

## 🚀 Why This Architecture?

✅ **Scalable**: S3 + OpenSearch handle millions of documents
✅ **Fast**: Vector search is O(log n) with proper indexing
✅ **Accurate**: Semantic search finds relevant content, not just keywords
✅ **Intelligent**: Claude Sonnet 4.5 provides human-like answers
✅ **Traceable**: Debug mode shows every agent step
✅ **Cost-Effective**: Pay only for what you use (AWS Bedrock pricing)

---

## 📝 Example End-to-End

**Input**: `clinical_trial_hypertension.pdf` (2 pages)

**Processing:**
1. Extract: 2 pages of text
2. Chunk: 15 chunks (500 chars each)
3. Embed: 15 vectors (1024 dimensions each)
4. Store: PDF in S3, 15 chunks in OpenSearch
5. Ready: Document ID `doc_abc123def456`

**Query**: "What are the primary endpoints?"

**Retrieval:**
- Query embedding: [0.234, -0.567, ...]
- Top 3 chunks:
  - Chunk 5: "Primary Endpoint: Reduction in systolic..."
  - Chunk 6: "...blood pressure by ≥10 mmHg from baseline..."
  - Chunk 12: "Secondary Endpoints: Reduction in diastolic..."

**Answer**: "The primary endpoint is a reduction in systolic blood pressure by ≥10 mmHg from baseline at Week 12."

**Citations**: Page 1, Chunks 5-6

---

**This is how MediQuery AI transforms a PDF into an intelligent Q&A system!** 🎉
