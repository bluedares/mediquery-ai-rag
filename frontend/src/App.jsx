import { useState, useEffect } from 'react'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  // State management
  const [uploadedDoc, setUploadedDoc] = useState(null)
  const [docSummary, setDocSummary] = useState(null)
  const [showSummary, setShowSummary] = useState(false)
  const [query, setQuery] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [showDebug, setShowDebug] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(null)
  const [availableDocs, setAvailableDocs] = useState([])
  const [showDocDropdown, setShowDocDropdown] = useState(false)
  const [loadingDocs, setLoadingDocs] = useState(false)
  const [conversationHistory, setConversationHistory] = useState([])
  const [expandedCitations, setExpandedCitations] = useState({})
  const [storageStats, setStorageStats] = useState(null)

  // Fetch available documents and storage stats on mount
  useEffect(() => {
    fetchAvailableDocs()
    fetchStorageStats()
  }, [])

  const fetchAvailableDocs = async () => {
    try {
      setLoadingDocs(true)
      const response = await axios.get(`${API_URL}/api/v1/documents`)
      setAvailableDocs(response.data.documents || [])
    } catch (err) {
      console.error('Failed to fetch documents:', err)
    } finally {
      setLoadingDocs(false)
    }
  }

  const fetchStorageStats = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/v1/storage/stats`)
      setStorageStats(response.data)
    } catch (err) {
      console.error('Failed to fetch storage stats:', err)
    }
  }

  const handleSelectExistingDoc = async (doc) => {
    setLoading(true)
    setShowDocDropdown(false)
    setError(null)
    
    try {
      // Fetch real summary from backend
      const response = await axios.get(`${API_URL}/api/v1/documents/${doc.document_id}/summary`)
      
      const summary = {
        title: response.data.title,
        pages: response.data.pages,
        chunks: response.data.chunks,
        healthIndicators: response.data.health_indicators.map(ind => ({
          name: ind.name,
          value: ind.value,
          status: ind.status,
          color: ind.color
        })),
        overallScore: response.data.overall_score,
        overallColor: response.data.overall_color,
        keyPoints: response.data.key_findings,
        stats: {
          documentId: doc.document_id,
          processingTime: 'AI Generated',
          modelUsed: 'Claude Sonnet 4.5 + BGE Embeddings'
        }
      }
      
      setUploadedDoc({
        id: doc.document_id,
        filename: doc.filename,
        pages: response.data.pages,
        chunks: response.data.chunks
      })
      setDocSummary(summary)
      setShowSummary(true)
      setLoading(false)
    } catch (err) {
      setLoading(false)
      setError(`Failed to load summary: ${err.response?.data?.detail || err.message}`)
      console.error('Summary fetch error:', err)
    }
  }

  const handleDeleteDoc = async (docId, e) => {
    e.stopPropagation()
    
    if (!window.confirm('Are you sure you want to delete this document?')) {
      return
    }

    try {
      await axios.delete(`${API_URL}/api/v1/documents/${docId}`)
      
      // Refresh document list
      await fetchAvailableDocs()
      
      // If deleted doc was currently selected, clear it
      if (uploadedDoc?.id === docId) {
        handleClearDocument()
      }
      
      alert('Document deleted successfully')
    } catch (err) {
      alert(`Failed to delete document: ${err.response?.data?.detail || err.message}`)
    }
  }

  const handleUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    const formData = new FormData()
    formData.append('file', file)

    setLoading(true)
    setError(null)
    setUploadProgress('uploading')

    const timeouts = []

    try {
      timeouts.push(setTimeout(() => setUploadProgress('tokenizing'), 500))
      timeouts.push(setTimeout(() => setUploadProgress('embedding'), 1500))
      timeouts.push(setTimeout(() => setUploadProgress('analyzing'), 3000))

      const response = await axios.post(`${API_URL}/api/v1/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      setUploadProgress('ready')

      // Fetch AI-generated summary
      setTimeout(async () => {
        try {
          const summaryResponse = await axios.get(`${API_URL}/api/v1/documents/${response.data.document_id}/summary`)
          
          const summary = {
            title: summaryResponse.data.title,
            pages: summaryResponse.data.pages,
            chunks: summaryResponse.data.chunks,
            healthIndicators: summaryResponse.data.health_indicators.map(ind => ({
              name: ind.name,
              value: ind.value,
              status: ind.status,
              color: ind.color
            })),
            overallScore: summaryResponse.data.overall_score,
            overallColor: summaryResponse.data.overall_color,
            keyPoints: summaryResponse.data.key_findings,
            stats: {
              documentId: response.data.document_id,
              processingTime: 'AI Generated',
              modelUsed: 'Claude Sonnet 4.5 + BGE Embeddings'
            }
          }
          
          setUploadedDoc({
            id: response.data.document_id,
            filename: response.data.filename,
            pages: summaryResponse.data.pages,
            chunks: summaryResponse.data.chunks
          })
          setDocSummary(summary)
          setShowSummary(true)
          setUploadProgress(null)
          setError(null)
          setLoading(false)
          
          // Refresh document list
          fetchAvailableDocs()
        } catch (summaryErr) {
          console.error('Failed to fetch summary:', summaryErr)
          // Fallback to basic info if summary fails
          setUploadedDoc({
            id: response.data.document_id,
            filename: response.data.filename,
            pages: response.data.pages,
            chunks: response.data.chunks
          })
          setShowSummary(false)
          setUploadProgress(null)
          setError('Document uploaded but summary generation failed')
          setLoading(false)
          fetchAvailableDocs()
          fetchStorageStats()  // Refresh storage stats after upload
        }
      }, 800)
    } catch (err) {
      timeouts.forEach(timeout => clearTimeout(timeout))
      setUploadProgress(null)
      setLoading(false)
      
      // Handle storage limit errors
      const errorDetail = err.response?.data?.detail
      if (errorDetail && typeof errorDetail === 'object' && errorDetail.message) {
        setError(errorDetail.message)
      } else {
        setError(errorDetail || err.message || 'Upload failed. Check backend logs.')
      }
      
      console.error('Upload error:', err)
      fetchStorageStats()  // Refresh stats on error
    }
  }

  const handleQuery = async (e) => {
    e.preventDefault()
    if (!query.trim() || !uploadedDoc) return

    const currentQuery = query.trim()
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await axios.post(`${API_URL}/api/v1/query`, {
        query: currentQuery,
        document_id: uploadedDoc.id,
        include_trace: true
      })
      
      // Add to conversation history
      setConversationHistory(prev => [...prev, {
        question: currentQuery,
        answer: response.data.answer,
        citations: response.data.citations || [],
        confidence: response.data.confidence,
        timestamp: new Date().toISOString()
      }])
      
      setResult(response.data)
      setQuery('') // Clear input after successful query
    } catch (err) {
      setError(err.response?.data?.detail?.message || err.message || 'Query failed')
    } finally {
      setLoading(false)
    }
  }

  const handleClearDocument = () => {
    setUploadedDoc(null)
    setDocSummary(null)
    setShowSummary(false)
    setQuery('')
    setResult(null)
    setError(null)
    setUploadProgress(null)
    setConversationHistory([]) // Clear conversation history
  }

  const handleProceedToQuery = () => {
    setShowSummary(false)
  }

  const examples = [
    "What are my key findings?",
    "Are my results normal?",
    "What should I be concerned about?"
  ]

  return (
    <div style={{ minHeight: '100vh', padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      {/* Header */}
      <header style={{ marginBottom: '30px', textAlign: 'center' }}>
        <h1 style={{ fontSize: '28px', fontWeight: 'bold', marginBottom: '8px' }}>
          🏥 MediQuery AI
        </h1>
        <p style={{ color: '#666', fontSize: '14px' }}>
          Multi-Agent RAG System • Claude Sonnet 4.6 • LangGraph
        </p>
        <button
          onClick={() => setShowDebug(!showDebug)}
          style={{
            marginTop: '12px',
            padding: '6px 16px',
            background: showDebug ? '#0284c7' : '#e5e7eb',
            color: showDebug ? 'white' : '#374151',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '13px',
            fontWeight: '500'
          }}
        >
          {showDebug ? '🐛 Debug ON' : '🐛 Debug OFF'}
        </button>
      </header>

      {/* Main Content */}
      <div style={{ display: 'grid', gridTemplateColumns: showDebug ? '1fr 1fr' : '1fr', gap: '20px' }}>

        {/* LEFT COLUMN — Upload / Summary / Query */}
        <div>
          {!uploadedDoc ? (
            /* UPLOAD STATE */
            <div style={{ maxWidth: '600px', margin: '0 auto' }}>
              <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
                <div style={{ fontSize: '48px', marginBottom: '20px' }}>📄</div>
                <h2 style={{ fontSize: '24px', fontWeight: '600', marginBottom: '12px' }}>
                  Upload Medical Document
                </h2>
                <p style={{ color: '#666', marginBottom: '12px' }}>
                  Upload a PDF to start asking questions
                </p>
                
                {/* Storage Stats */}
                {storageStats && (
                  <div style={{
                    marginBottom: '24px',
                    padding: '12px 16px',
                    background: storageStats.usage_percent >= 80 ? '#fef2f2' : '#f0fdf4',
                    border: `1px solid ${storageStats.usage_percent >= 80 ? '#fecaca' : '#bbf7d0'}`,
                    borderRadius: '8px',
                    fontSize: '13px'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                      <span style={{ fontWeight: '600', color: storageStats.usage_percent >= 80 ? '#991b1b' : '#166534' }}>
                        📊 Storage: {storageStats.document_count}/{storageStats.max_documents} documents
                      </span>
                      <span style={{ color: storageStats.usage_percent >= 80 ? '#991b1b' : '#166534' }}>
                        {storageStats.usage_percent}% used
                      </span>
                    </div>
                    <div style={{ 
                      width: '100%', 
                      height: '6px', 
                      background: '#e5e7eb', 
                      borderRadius: '3px',
                      overflow: 'hidden'
                    }}>
                      <div style={{
                        width: `${storageStats.usage_percent}%`,
                        height: '100%',
                        background: storageStats.usage_percent >= 80 ? '#dc2626' : '#10b981',
                        transition: 'width 0.3s ease'
                      }} />
                    </div>
                    {storageStats.usage_percent >= 80 && (
                      <div style={{ marginTop: '8px', color: '#991b1b', fontSize: '12px' }}>
                        ⚠️ Storage almost full! Delete old documents to upload new ones.
                      </div>
                    )}
                    {storageStats.documents_remaining === 0 && (
                      <div style={{ marginTop: '8px', color: '#991b1b', fontSize: '12px', fontWeight: '600' }}>
                        🚫 Storage limit reached! Please delete documents before uploading.
                      </div>
                    )}
                  </div>
                )}

                {/* Existing Documents Dropdown */}
                {availableDocs.length > 0 && (
                  <div style={{ marginBottom: '20px' }}>
                    <button
                      onClick={() => setShowDocDropdown(!showDocDropdown)}
                      style={{
                        width: '100%',
                        padding: '12px 16px',
                        background: '#f3f4f6',
                        border: '1px solid #d1d5db',
                        borderRadius: '8px',
                        cursor: 'pointer',
                        fontSize: '14px',
                        fontWeight: '500',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center'
                      }}
                    >
                      <span>� Recent Reports ({availableDocs.length})</span>
                      <span>{showDocDropdown ? '▲' : '▼'}</span>
                    </button>

                    {showDocDropdown && (
                      <div style={{
                        marginTop: '8px',
                        border: '1px solid #d1d5db',
                        borderRadius: '8px',
                        background: 'white',
                        maxHeight: '200px',
                        overflowY: 'auto'
                      }}>
                        {availableDocs.map((doc) => (
                          <div
                            key={doc.document_id}
                            onClick={() => handleSelectExistingDoc(doc)}
                            style={{
                              padding: '12px 16px',
                              display: 'flex',
                              justifyContent: 'space-between',
                              alignItems: 'center',
                              cursor: 'pointer',
                              borderBottom: '1px solid #f3f4f6',
                              transition: 'background 0.2s'
                            }}
                            onMouseEnter={(e) => e.currentTarget.style.background = '#f9fafb'}
                            onMouseLeave={(e) => e.currentTarget.style.background = 'white'}
                          >
                            <span style={{ fontSize: '14px', flex: 1, textAlign: 'left' }}>
                              📄 {doc.filename}
                            </span>
                            <button
                              onClick={(e) => handleDeleteDoc(doc.document_id, e)}
                              style={{
                                padding: '4px 8px',
                                background: '#fee2e2',
                                color: '#dc2626',
                                border: 'none',
                                borderRadius: '4px',
                                cursor: 'pointer',
                                fontSize: '12px',
                                fontWeight: '600'
                              }}
                              onMouseEnter={(e) => e.currentTarget.style.background = '#fecaca'}
                              onMouseLeave={(e) => e.currentTarget.style.background = '#fee2e2'}
                            >
                              ✕
                            </button>
                          </div>
                        ))}
                      </div>
                    )}

                    <div style={{
                      margin: '20px 0',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '12px'
                    }}>
                      <div style={{ flex: 1, height: '1px', background: '#e5e7eb' }}></div>
                      <span style={{ color: '#9ca3af', fontSize: '14px', fontWeight: '500' }}>OR</span>
                      <div style={{ flex: 1, height: '1px', background: '#e5e7eb' }}></div>
                    </div>
                  </div>
                )}

                <input
                  type="file"
                  accept=".pdf"
                  onChange={handleUpload}
                  disabled={loading}
                  style={{ display: 'none' }}
                  id="file-upload"
                />

                <label
                  htmlFor="file-upload"
                  style={{
                    display: 'inline-block',
                    padding: '12px 32px',
                    background: loading ? '#9ca3af' : '#0284c7',
                    color: 'white',
                    borderRadius: '8px',
                    cursor: loading ? 'not-allowed' : 'pointer',
                    fontSize: '16px',
                    fontWeight: '500'
                  }}
                >
                  {loading ? '⏳ Processing...' : '📤 Choose PDF File'}
                </label>

                {/* Upload Progress Stages */}
                {uploadProgress && (
                  <div style={{
                    marginTop: '24px',
                    padding: '20px',
                    background: '#eff6ff',
                    border: '1px solid #bfdbfe',
                    borderRadius: '8px'
                  }}>
                    <div style={{ marginBottom: '16px', fontSize: '14px', fontWeight: '600', color: '#1e40af' }}>
                      Processing Document...
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                      {/* Uploading */}
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <div style={{
                          width: '24px', height: '24px', borderRadius: '50%',
                          background: uploadProgress === 'uploading' ? '#3b82f6' : '#10b981',
                          color: 'white', display: 'flex', alignItems: 'center',
                          justifyContent: 'center', fontSize: '12px'
                        }}>
                          {uploadProgress === 'uploading' ? '⏳' : '✓'}
                        </div>
                        <span style={{ fontSize: '14px', color: uploadProgress === 'uploading' ? '#1e40af' : '#6b7280' }}>
                          Uploading PDF
                        </span>
                      </div>

                      {/* Tokenizing */}
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <div style={{
                          width: '24px', height: '24px', borderRadius: '50%',
                          background: uploadProgress === 'tokenizing' ? '#3b82f6' :
                            ['embedding', 'analyzing', 'ready'].includes(uploadProgress) ? '#10b981' : '#e5e7eb',
                          color: uploadProgress === 'tokenizing' || ['embedding', 'analyzing', 'ready'].includes(uploadProgress) ? 'white' : '#9ca3af',
                          display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '12px'
                        }}>
                          {uploadProgress === 'tokenizing' ? '⏳' :
                            ['embedding', 'analyzing', 'ready'].includes(uploadProgress) ? '✓' : '○'}
                        </div>
                        <span style={{
                          fontSize: '14px',
                          color: uploadProgress === 'tokenizing' ? '#1e40af' :
                            ['embedding', 'analyzing', 'ready'].includes(uploadProgress) ? '#6b7280' : '#9ca3af'
                        }}>
                          Creating Chunks
                        </span>
                      </div>

                      {/* Embedding */}
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <div style={{
                          width: '24px', height: '24px', borderRadius: '50%',
                          background: uploadProgress === 'embedding' ? '#3b82f6' :
                            ['analyzing', 'ready'].includes(uploadProgress) ? '#10b981' : '#e5e7eb',
                          color: uploadProgress === 'embedding' || ['analyzing', 'ready'].includes(uploadProgress) ? 'white' : '#9ca3af',
                          display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '12px'
                        }}>
                          {uploadProgress === 'embedding' ? '⏳' :
                            ['analyzing', 'ready'].includes(uploadProgress) ? '✓' : '○'}
                        </div>
                        <span style={{
                          fontSize: '14px',
                          color: uploadProgress === 'embedding' ? '#1e40af' :
                            ['analyzing', 'ready'].includes(uploadProgress) ? '#6b7280' : '#9ca3af'
                        }}>
                          Creating Embeddings
                        </span>
                      </div>

                      {/* Analyzing */}
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <div style={{
                          width: '24px', height: '24px', borderRadius: '50%',
                          background: uploadProgress === 'analyzing' ? '#3b82f6' :
                            uploadProgress === 'ready' ? '#10b981' : '#e5e7eb',
                          color: uploadProgress === 'analyzing' || uploadProgress === 'ready' ? 'white' : '#9ca3af',
                          display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '12px'
                        }}>
                          {uploadProgress === 'analyzing' ? '⏳' :
                            uploadProgress === 'ready' ? '✓' : '○'}
                        </div>
                        <span style={{
                          fontSize: '14px',
                          color: uploadProgress === 'analyzing' ? '#1e40af' :
                            uploadProgress === 'ready' ? '#6b7280' : '#9ca3af'
                        }}>
                          Analyzing Report
                        </span>
                      </div>

                      {/* Ready */}
                      {uploadProgress === 'ready' && (
                        <div style={{
                          marginTop: '8px', padding: '12px', background: '#d1fae5',
                          borderRadius: '6px', fontSize: '14px', fontWeight: '600',
                          color: '#065f46', textAlign: 'center'
                        }}>
                          ✅ Ready! You can now ask questions
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {error && (
                  <div style={{
                    marginTop: '20px', padding: '12px', background: '#fef2f2',
                    border: '1px solid #fecaca', borderRadius: '6px',
                    color: '#991b1b', fontSize: '14px'
                  }}>
                    ❌ {error}
                  </div>
                )}

                <div style={{ marginTop: '32px', fontSize: '13px', color: '#999' }}>
                  <p>Supported: PDF files</p>
                  <p style={{ marginTop: '4px' }}>Max size: 10MB</p>
                </div>
              </div>
            </div>

          ) : showSummary && docSummary ? (
            /* SUMMARY STATE */
            <div style={{ maxWidth: '800px', margin: '0 auto' }}>
              <div className="card" style={{ padding: '40px' }}>
                <div style={{ textAlign: 'center', marginBottom: '32px' }}>
                  <div style={{ fontSize: '48px', marginBottom: '16px' }}>✅</div>
                  <h2 style={{ fontSize: '24px', fontWeight: '600', marginBottom: '8px' }}>
                    Document Processed Successfully!
                  </h2>
                  <p style={{ color: '#666', fontSize: '14px' }}>{docSummary.title}</p>
                </div>

                <div style={{ marginBottom: '32px' }}>
                  <h3 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '16px', color: '#374151' }}>
                    📊 Report Summary
                  </h3>
                  {/* Removed pages/chunks display - now in debug panel only */}

                  {/* Health Indicators */}
                  <div style={{
                    padding: '20px', background: '#f9fafb',
                    border: '1px solid #e5e7eb', borderRadius: '8px', marginBottom: '16px'
                  }}>
                    <h4 style={{ fontSize: '14px', fontWeight: '600', marginBottom: '16px', color: '#374151' }}>
                      🏥 Health Indicators
                    </h4>
                    
                    {docSummary.healthIndicators && docSummary.healthIndicators.length > 0 ? (
                      <>
                        {docSummary.healthIndicators.map((indicator, i) => (
                          <div key={i} style={{ marginBottom: '16px' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                              <span style={{ fontSize: '14px', fontWeight: '500', color: '#374151' }}>
                                {indicator.name}
                              </span>
                              <span style={{ 
                                fontSize: '14px', 
                                fontWeight: '700', 
                                color: indicator.color,
                                padding: '2px 8px',
                                background: indicator.color + '20',
                                borderRadius: '4px'
                              }}>
                                {indicator.value}%
                              </span>
                            </div>
                            <div style={{
                              width: '100%', height: '10px', background: '#e5e7eb',
                              borderRadius: '5px', overflow: 'hidden', boxShadow: 'inset 0 1px 2px rgba(0,0,0,0.1)'
                            }}>
                              <div style={{
                                width: `${indicator.value}%`, height: '100%',
                                background: `linear-gradient(90deg, ${indicator.color}, ${indicator.color}dd)`,
                                transition: 'width 0.5s ease-out',
                                boxShadow: '0 1px 2px rgba(0,0,0,0.1)'
                              }} />
                            </div>
                            <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '4px' }}>
                              Status: <span style={{ fontWeight: '600', color: indicator.color }}>
                                {indicator.status.charAt(0).toUpperCase() + indicator.status.slice(1)}
                              </span>
                            </div>
                          </div>
                        ))}
                        
                        <div style={{
                          marginTop: '20px', padding: '16px', 
                          background: `linear-gradient(135deg, ${docSummary.overallColor}15, ${docSummary.overallColor}05)`,
                          border: `2px solid ${docSummary.overallColor}`,
                          borderRadius: '8px', textAlign: 'center'
                        }}>
                          <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px' }}>
                            Overall Health Score
                          </div>
                          <div style={{ fontSize: '24px', fontWeight: '700', color: docSummary.overallColor }}>
                            {docSummary.overallScore}
                          </div>
                        </div>
                      </>
                    ) : (
                      <div style={{
                        padding: '24px', textAlign: 'center',
                        background: '#fef3c7', border: '1px solid #fbbf24',
                        borderRadius: '8px'
                      }}>
                        <div style={{ fontSize: '32px', marginBottom: '8px' }}>📋</div>
                        <div style={{ fontSize: '14px', fontWeight: '600', color: '#92400e', marginBottom: '4px' }}>
                          No Health Metrics Found
                        </div>
                        <div style={{ fontSize: '13px', color: '#78350f' }}>
                          This document doesn't contain standard health indicators like blood pressure, glucose, cholesterol, etc.
                        </div>
                        {docSummary.overallScore && (
                          <div style={{
                            marginTop: '12px', padding: '12px',
                            background: 'white', borderRadius: '6px'
                          }}>
                            <span style={{ fontSize: '13px', color: '#6b7280' }}>Document Status: </span>
                            <span style={{ fontSize: '16px', fontWeight: '600', color: docSummary.overallColor }}>
                              {docSummary.overallScore}
                            </span>
                          </div>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Key Findings */}
                  {docSummary.keyPoints && docSummary.keyPoints.length > 0 ? (
                    <div style={{
                      padding: '20px', background: '#eff6ff',
                      border: '1px solid #bfdbfe', borderRadius: '8px', marginBottom: '16px'
                    }}>
                      <h4 style={{ fontSize: '14px', fontWeight: '600', marginBottom: '16px', color: '#1e40af' }}>
                        🔍 Key Findings
                      </h4>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                        {docSummary.keyPoints.map((point, i) => (
                          <div key={i} style={{
                            display: 'flex', alignItems: 'start', gap: '12px',
                            padding: '12px', background: 'white',
                            borderRadius: '6px', border: '1px solid #dbeafe'
                          }}>
                            <div style={{
                              minWidth: '24px', height: '24px',
                              background: '#3b82f6', color: 'white',
                              borderRadius: '50%', display: 'flex',
                              alignItems: 'center', justifyContent: 'center',
                              fontSize: '12px', fontWeight: '600'
                            }}>
                              {i + 1}
                            </div>
                            <div style={{ fontSize: '14px', color: '#1e40af', lineHeight: '1.5' }}>
                              {point}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <div style={{
                      padding: '20px', background: '#f3f4f6',
                      border: '1px solid #d1d5db', borderRadius: '8px', marginBottom: '16px',
                      textAlign: 'center'
                    }}>
                      <div style={{ fontSize: '14px', color: '#6b7280' }}>
                        📝 No key findings extracted from this document
                      </div>
                    </div>
                  )}

                  <div style={{ fontSize: '12px', color: '#6b7280', padding: '12px', background: '#f9fafb', borderRadius: '6px' }}>
                    <div><strong>Document ID:</strong> {docSummary.stats.documentId}</div>
                    <div style={{ marginTop: '4px' }}><strong>AI Model:</strong> {docSummary.stats.modelUsed}</div>
                  </div>
                </div>

                <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
                  <button
                    onClick={handleProceedToQuery}
                    style={{
                      padding: '12px 32px', background: '#0284c7', color: 'white',
                      border: 'none', borderRadius: '8px', cursor: 'pointer',
                      fontSize: '16px', fontWeight: '500'
                    }}
                  >
                    🚀 Start Asking Questions
                  </button>
                  <button
                    onClick={handleClearDocument}
                    style={{
                      padding: '12px 24px', background: '#e5e7eb', color: '#374151',
                      border: 'none', borderRadius: '8px', cursor: 'pointer',
                      fontSize: '14px', fontWeight: '500'
                    }}
                  >
                    ✕ Upload Different PDF
                  </button>
                </div>
              </div>
            </div>

          ) : (
            /* QUERY STATE - Chat Interface */
            <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 180px)' }}>
              {/* Document Info Card - Fixed at top */}
              <div className="card" style={{ marginBottom: '16px', background: '#f0fdf4', border: '1px solid #bbf7d0', flexShrink: 0 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                  <div>
                    <div style={{ fontSize: '14px', fontWeight: '600', color: '#166534', marginBottom: '8px' }}>
                      ✅ Document Ready
                    </div>
                    <div style={{ fontSize: '13px', color: '#15803d' }}>
                      📄 {uploadedDoc.filename}<br />
                      📊 {uploadedDoc.pages} pages • {uploadedDoc.chunks} chunks
                    </div>
                  </div>
                  <button
                    onClick={handleClearDocument}
                    style={{
                      padding: '6px 12px', background: '#dc2626', color: 'white',
                      border: 'none', borderRadius: '6px', cursor: 'pointer',
                      fontSize: '12px', fontWeight: '500'
                    }}
                  >
                    ✕ Clear & Upload New
                  </button>
                </div>
              </div>

              {/* Conversation Area - Scrollable */}
              <div style={{
                flex: 1,
                overflowY: 'auto',
                marginBottom: '16px',
                padding: '16px',
                background: '#f9fafb',
                borderRadius: '8px',
                border: '1px solid #e5e7eb'
              }}>
                {conversationHistory.length === 0 ? (
                  <div style={{ textAlign: 'center', padding: '40px 20px', color: '#6b7280' }}>
                    <div style={{ fontSize: '48px', marginBottom: '16px' }}>💬</div>
                    <div style={{ fontSize: '16px', fontWeight: '500', marginBottom: '8px' }}>
                      Start a conversation
                    </div>
                    <div style={{ fontSize: '14px' }}>
                      Ask questions about your medical report below
                    </div>
                  </div>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                    {conversationHistory.map((item, idx) => (
                      <div key={idx}>
                        {/* Question */}
                        <div style={{
                          display: 'flex',
                          justifyContent: 'flex-end',
                          marginBottom: '12px'
                        }}>
                          <div style={{
                            maxWidth: '80%',
                            padding: '12px 16px',
                            background: '#0284c7',
                            color: 'white',
                            borderRadius: '12px 12px 4px 12px',
                            fontSize: '14px',
                            lineHeight: '1.5'
                          }}>
                            <div style={{ fontWeight: '500', marginBottom: '4px', opacity: 0.9, fontSize: '12px' }}>
                              You asked:
                            </div>
                            {item.question}
                          </div>
                        </div>

                        {/* Answer */}
                        <div style={{
                          display: 'flex',
                          justifyContent: 'flex-start'
                        }}>
                          <div style={{
                            maxWidth: '85%',
                            padding: '16px',
                            background: 'white',
                            border: '1px solid #e5e7eb',
                            borderRadius: '12px 12px 12px 4px',
                            fontSize: '14px'
                          }}>
                            <div style={{
                              display: 'flex',
                              alignItems: 'center',
                              gap: '8px',
                              marginBottom: '12px',
                              paddingBottom: '8px',
                              borderBottom: '1px solid #e5e7eb'
                            }}>
                              <div style={{ fontSize: '20px' }}>🤖</div>
                              <div style={{ fontWeight: '600', color: '#374151' }}>AI Assistant</div>
                              <div style={{
                                marginLeft: 'auto',
                                fontSize: '11px',
                                color: '#6b7280',
                                background: '#f3f4f6',
                                padding: '2px 8px',
                                borderRadius: '4px'
                              }}>
                                {(item.confidence * 100).toFixed(0)}% confident
                              </div>
                            </div>
                            
                            <div style={{ lineHeight: '1.8', color: '#374151', marginBottom: '12px', whiteSpace: 'pre-wrap' }}>
                              {item.answer}
                            </div>

                            {item.citations && item.citations.length > 0 && (
                              <div style={{ marginTop: '12px', paddingTop: '12px', borderTop: '1px solid #e5e7eb' }}>
                                <button
                                  onClick={() => setExpandedCitations(prev => ({
                                    ...prev,
                                    [idx]: !prev[idx]
                                  }))}
                                  style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '6px',
                                    fontSize: '12px',
                                    fontWeight: '600',
                                    color: '#6b7280',
                                    background: 'none',
                                    border: 'none',
                                    cursor: 'pointer',
                                    padding: '4px 0',
                                    marginBottom: '8px'
                                  }}
                                >
                                  <span>{expandedCitations[idx] ? '▼' : '▶'}</span>
                                  <span>📚 Sources ({item.citations.length})</span>
                                </button>
                                
                                {expandedCitations[idx] && (
                                  <div>
                                    {item.citations.map((cite, i) => (
                                      <div key={i} style={{
                                        padding: '8px',
                                        background: '#f9fafb',
                                        border: '1px solid #e5e7eb',
                                        borderRadius: '6px',
                                        marginBottom: '6px',
                                        fontSize: '12px'
                                      }}>
                                        <div style={{ fontWeight: '500', marginBottom: '4px', color: '#374151' }}>
                                          Page {cite.page} • {(cite.relevance_score * 100).toFixed(0)}% relevant
                                        </div>
                                        <div style={{ color: '#6b7280', fontSize: '11px' }}>{cite.text}</div>
                                      </div>
                                    ))}
                                  </div>
                                )}
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Input Area - Fixed at bottom */}
              <div className="card" style={{ flexShrink: 0, padding: '16px' }}>
                <form onSubmit={handleQuery}>
                  <div style={{ marginBottom: '12px' }}>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '12px' }}>
                      <span style={{ fontSize: '12px', color: '#6b7280', alignSelf: 'center', marginRight: '4px' }}>
                        Quick examples:
                      </span>
                      {examples.map((ex, i) => (
                        <button
                          key={i}
                          type="button"
                          onClick={() => setQuery(ex)}
                          style={{
                            padding: '4px 10px',
                            fontSize: '11px',
                            background: '#f3f4f6',
                            border: '1px solid #e5e7eb',
                            borderRadius: '6px',
                            cursor: 'pointer',
                            color: '#374151'
                          }}
                        >
                          {ex}
                        </button>
                      ))}
                    </div>
                    
                    <div style={{ display: 'flex', gap: '8px', alignItems: 'end' }}>
                      <textarea
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="Ask about the document..."
                        disabled={loading}
                        rows={2}
                        style={{
                          flex: 1,
                          padding: '12px',
                          border: '1px solid #d1d5db',
                          borderRadius: '8px',
                          fontSize: '14px',
                          resize: 'none',
                          fontFamily: 'inherit'
                        }}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault()
                            handleQuery(e)
                          }
                        }}
                      />
                      <button
                        type="submit"
                        disabled={loading || !query.trim()}
                        style={{
                          padding: '12px 24px',
                          background: loading || !query.trim() ? '#d1d5db' : '#0284c7',
                          color: 'white',
                          border: 'none',
                          borderRadius: '8px',
                          cursor: loading || !query.trim() ? 'not-allowed' : 'pointer',
                          fontSize: '14px',
                          fontWeight: '500',
                          whiteSpace: 'nowrap'
                        }}
                      >
                        {loading ? '⏳ Retrieving chunks...' : '🚀 Ask'}
                      </button>
                    </div>
                  </div>

                  {error && (
                    <div style={{
                      padding: '10px 12px',
                      background: '#fef2f2',
                      border: '1px solid #fecaca',
                      borderRadius: '6px',
                      color: '#991b1b',
                      fontSize: '13px'
                    }}>
                      ❌ {error}
                    </div>
                  )}
                </form>
              </div>
            </div>
          )}
        </div>
        {/* END LEFT COLUMN */}

        {/* RIGHT COLUMN — Debug Panel */}
        {showDebug && (
          <div className="card" style={{ height: 'fit-content', position: 'sticky', top: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
              <h2 style={{ fontSize: '18px', fontWeight: '600', margin: 0 }}>
                🐛 Debug Logs
              </h2>
              {result?.agent_trace && (
                <button
                  onClick={() => {
                    const debugText = JSON.stringify({
                      request_id: result.request_id,
                      agent_trace: result.agent_trace,
                      processing_time_ms: result.processing_time_ms,
                      confidence: result.confidence,
                      answer: result.answer,
                      citations: result.citations
                    }, null, 2);
                    navigator.clipboard.writeText(debugText);
                    alert('Debug logs copied to clipboard!');
                  }}
                  style={{
                    padding: '6px 12px',
                    background: '#0284c7',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '12px',
                    fontWeight: '500'
                  }}
                >
                  � Copy Logs
                </button>
              )}
            </div>

            {loading && (
              <div style={{ textAlign: 'center', padding: '20px', color: '#666' }}>
                <div style={{ fontSize: '24px', marginBottom: '8px' }}>⏳</div>
                <div>Retrieving chunks from vector DB...</div>
              </div>
            )}

            {!loading && !result && (
              <div style={{ textAlign: 'center', padding: '20px', color: '#999' }}>
                Submit a query to see agent logs
              </div>
            )}

            {result?.agent_trace && (
              <div>
                {result.agent_trace.map((trace, i) => (
                  <div key={i} style={{
                    padding: '10px',
                    background: trace.status === 'success' ? '#f0fdf4' : '#fef2f2',
                    border: `1px solid ${trace.status === 'success' ? '#bbf7d0' : '#fecaca'}`,
                    borderRadius: '4px', marginBottom: '8px', fontSize: '12px'
                  }}>
                    <div style={{ fontWeight: '600', marginBottom: '4px' }}>
                      {trace.status === 'success' ? '✅' : '❌'} {trace.agent}
                    </div>
                    <div style={{ color: '#666' }}>⏱️ {trace.duration_ms?.toFixed(0)}ms</div>
                    {trace.input_summary && (
                      <div style={{ marginTop: '4px', fontSize: '11px', color: '#666' }}>
                        Input: {trace.input_summary}
                      </div>
                    )}
                  </div>
                ))}

                <div style={{
                  marginTop: '12px', padding: '10px',
                  background: '#f3f4f6', borderRadius: '4px', fontSize: '12px'
                }}>
                  <div><strong>Total Steps:</strong> {result.agent_trace.length}</div>
                  <div><strong>Total Time:</strong> {result.agent_trace.reduce((sum, t) => sum + (t.duration_ms || 0), 0).toFixed(0)}ms</div>
                  <div><strong>Request ID:</strong> {result.request_id?.slice(0, 8)}...</div>
                </div>
              </div>
            )}
          </div>
        )}
        {/* END RIGHT COLUMN */}

      </div>
      {/* END MAIN GRID */}

      {/* Footer */}
      <footer style={{
        marginTop: '40px', paddingTop: '20px',
        borderTop: '1px solid #e5e7eb', textAlign: 'center',
        fontSize: '12px', color: '#999'
      }}>
        <p>Built for Indegene Interview • March 2026</p>
        <p style={{ marginTop: '4px' }}>Backend: FastAPI + AWS Bedrock + OpenSearch + LangGraph</p>
      </footer>
    </div>
  )
}

export default App
