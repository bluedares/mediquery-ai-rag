# Implementation Plan: Document Dropdown with Delete Feature

## 🎯 Goal
Allow users to select previously uploaded PDFs from a dropdown instead of re-uploading. Include delete functionality for each document.

## 📋 Current State Analysis

### Frontend State (App.jsx)
- `uploadedDoc`: Currently selected document {id, filename, pages, chunks}
- `docSummary`: Summary after upload
- `showSummary`: Boolean to show summary screen
- Upload flow: Upload → Summary → Query

### Backend Existing
- ✅ S3Service has `list_files(prefix)` method
- ✅ S3Service has `delete_file(key)` method
- ✅ Upload endpoint: POST `/api/v1/upload`
- ❌ Missing: List documents endpoint
- ❌ Missing: Delete document endpoint
- ❌ Missing: Document metadata storage (we only have S3 files, no metadata about pages/chunks)

## 🔧 Implementation Steps

### Step 1: Create Backend Endpoints (NEW FILE)
**File**: `backend/app/api/documents.py`

```python
# GET /api/v1/documents - List all uploaded documents
# DELETE /api/v1/documents/{doc_id} - Delete document from S3 and OpenSearch
```

**Response Model**:
```python
{
  "documents": [
    {
      "document_id": "doc_abc123",
      "filename": "diabetes_study.pdf",
      "uploaded_at": "2026-03-05T14:35:30Z",
      "s3_key": "documents/doc_abc123.pdf"
    }
  ]
}
```

**Challenge**: We don't store metadata (pages, chunks) separately. 
**Solution**: Parse from S3 object metadata or return basic info only.

### Step 2: Register New Router
**File**: `backend/app/main.py`
- Import documents router
- Add `app.include_router(documents.router, prefix="/api/v1", tags=["documents"])`

### Step 3: Update Frontend State
**File**: `frontend/src/App.jsx`

**New State**:
```javascript
const [availableDocs, setAvailableDocs] = useState([]) // List of uploaded docs
const [showDocDropdown, setShowDocDropdown] = useState(false) // Toggle dropdown
```

**New Functions**:
```javascript
const fetchAvailableDocs = async () => {
  // GET /api/v1/documents
  // Update availableDocs state
}

const handleSelectExistingDoc = async (doc) => {
  // Set uploadedDoc from selected doc
  // Skip summary, go directly to query interface
}

const handleDeleteDoc = async (docId) => {
  // DELETE /api/v1/documents/{docId}
  // Refresh availableDocs list
  // If deleted doc was selected, clear uploadedDoc
}
```

### Step 4: Update Upload UI
**Location**: Upload state section (lines ~155-240)

**Current**:
```
[Upload Button]
```

**New Design**:
```
┌─────────────────────────────────────┐
│  📄 Upload Medical Document         │
│                                     │
│  [▼ Select Existing Document]      │  <- Dropdown button
│                                     │
│  ────────── OR ──────────           │
│                                     │
│  [📤 Choose PDF File]               │  <- Upload new
└─────────────────────────────────────┘
```

**When dropdown expanded**:
```
┌─────────────────────────────────────┐
│  [▲ Select Existing Document]       │
│  ┌───────────────────────────────┐  │
│  │ 📄 diabetes_study.pdf      [X]│  │  <- Delete button
│  │ 📄 clinical_trial.pdf      [X]│  │
│  │ 📄 hypertension.pdf        [X]│  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

### Step 5: UI Component Structure

**Dropdown Item**:
```jsx
<div onClick={() => handleSelectExistingDoc(doc)}>
  <span>📄 {doc.filename}</span>
  <button onClick={(e) => {
    e.stopPropagation(); // Prevent selecting when deleting
    handleDeleteDoc(doc.document_id);
  }}>
    ✕
  </button>
</div>
```

## ⚠️ Important Considerations

1. **Don't Break Existing Flow**
   - Keep upload button working as-is
   - Selecting existing doc should skip summary, go to query
   - Maintain all existing state management

2. **Delete Confirmation**
   - Add `window.confirm()` before deleting
   - Show loading state during delete

3. **Error Handling**
   - Handle empty document list gracefully
   - Show error if list/delete fails
   - Refresh list after delete

4. **Styling**
   - Match existing card/button styles
   - Use existing color scheme
   - Keep responsive design

5. **Backend Cleanup**
   - Delete from S3
   - Delete from OpenSearch (all chunks)
   - Return success/error properly

## 🧪 Testing Checklist

- [ ] List documents shows all uploaded PDFs
- [ ] Selecting existing doc loads it correctly
- [ ] Delete removes from S3 and UI
- [ ] Delete confirmation works
- [ ] Upload new doc still works
- [ ] Dropdown toggles properly
- [ ] Error handling works
- [ ] UI doesn't break on mobile
- [ ] Debug panel still works

## 📝 Files to Modify

1. **NEW**: `backend/app/api/documents.py` (list & delete endpoints)
2. **EDIT**: `backend/app/main.py` (register router)
3. **EDIT**: `frontend/src/App.jsx` (add dropdown UI + state)

## 🚀 Implementation Order

1. Backend endpoints (documents.py)
2. Register router (main.py)
3. Test endpoints with curl
4. Frontend state + fetch function
5. Frontend dropdown UI
6. Frontend delete functionality
7. Full integration test
