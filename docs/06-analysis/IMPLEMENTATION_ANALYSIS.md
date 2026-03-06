# Implementation Analysis & Plan

## Current Issues

### 1. Hardcoded Health Indicators
**Problem**: Health indicators (80%, 60%, 40%) are hardcoded in frontend
**Location**: `frontend/src/App.jsx` lines 127-131 and 44-48
**Solution**: Generate real summary using LLM from document content

### 2. Wrong Page/Chunk Values
**Problem**: Showing 1 page instead of actual 15 pages
**Cause**: `handleSelectExistingDoc` uses hardcoded values (pages: 1, chunks: 3)
**Location**: `frontend/src/App.jsx` lines 65-67
**Solution**: Fetch actual metadata from backend

### 3. Pages/Chunks Display
**Problem**: User doesn't want to see pages/chunks in summary
**Solution**: Move to debug panel only, show only health summary

## Current Architecture

### Document Storage
```
Upload Flow:
1. PDF uploaded → Extract text → Create chunks
2. Generate embeddings per chunk
3. Store PDF in S3: s3://mediquery-documents/documents/{doc_id}.pdf
4. Index chunks in OpenSearch with metadata:
   - document_id: unique per document
   - chunk_id: unique per chunk
   - page: page number
   - text: chunk text
   - embedding: vector embedding
```

### Embedding Isolation
✅ **CONFIRMED**: Each document has unique document_id
✅ **CONFIRMED**: Chunks are indexed with document_id in metadata
✅ **CONFIRMED**: Query filters by document_id, so embeddings are isolated

**Evidence from upload.py**:
```python
opensearch_service.index_document(
    index_name="medical-documents",
    doc_id=f"{document_id}_{chunk['chunk_id']}",  # Unique per doc+chunk
    metadata={
        'document_id': document_id,  # Filters queries to this doc only
        'page': chunk['page'],
        'chunk_id': chunk['chunk_id']
    }
)
```

## Proposed Solution

### 1. Create Summary Generation Endpoint
**New Endpoint**: `GET /api/v1/documents/{doc_id}/summary`

**Flow**:
1. Retrieve all chunks for document_id from OpenSearch
2. Combine chunk texts
3. Send to Claude Sonnet 4.5 with prompt:
   ```
   Analyze this medical report and provide:
   1. Health indicators with scores (0-100%)
   2. Overall health assessment
   3. Key findings
   ```
4. Parse LLM response and return structured summary

### 2. Update Frontend
**Changes**:
- Remove hardcoded health indicators
- Call `/api/v1/documents/{doc_id}/summary` when document selected
- Show loading state while generating summary
- Remove pages/chunks from summary UI
- Add pages/chunks to debug panel

### 3. Backend Implementation

**File**: `backend/app/api/documents.py`
```python
@router.get("/documents/{document_id}/summary")
async def get_document_summary(document_id: str):
    # 1. Retrieve chunks from OpenSearch
    # 2. Generate summary using Bedrock Claude
    # 3. Return structured summary with health indicators
```

**File**: `backend/app/services/bedrock.py` (new)
```python
class BedrockService:
    async def generate_summary(self, document_text: str):
        # Call Claude Sonnet 4.5 to analyze medical report
        # Return health indicators and summary
```

## Benefits
1. ✅ Real AI-generated summaries
2. ✅ Accurate health indicators from document content
3. ✅ Embeddings remain isolated per document
4. ✅ Cleaner UI (no technical metadata)
5. ✅ Debug panel shows technical details

## Implementation Steps
1. Create Bedrock service for LLM calls
2. Add summary endpoint to documents.py
3. Update frontend to call summary endpoint
4. Remove hardcoded data
5. Move pages/chunks to debug panel
6. Test with real medical reports
