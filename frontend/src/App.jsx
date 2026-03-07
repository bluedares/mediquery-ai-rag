import { useState, useEffect, useRef } from 'react'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Add mobile-responsive styles and animations
const mobileStyles = `
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
  
  @media (max-width: 768px) {
    .card {
      padding: 16px !important;
      margin: 8px !important;
    }
    
    .mobile-stack {
      flex-direction: column !important;
    }
    
    .mobile-full-width {
      width: 100% !important;
      max-width: 100% !important;
    }
    
    .mobile-text-sm {
      font-size: 12px !important;
    }
    
    .mobile-hide {
      display: none !important;
    }
    
    .mobile-padding-sm {
      padding: 8px !important;
    }
  }
`

// Inject styles
if (typeof document !== 'undefined') {
  const styleSheet = document.createElement('style')
  styleSheet.textContent = mobileStyles
  document.head.appendChild(styleSheet)
}

function App() {
  console.log('🚀 MediQuery App Loaded - Build v3.0')
  
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
  
  // Refs for Q&A section to enable auto-scroll
  const qaInputRef = useRef(null)
  const qaConversationRef = useRef(null)
  const latestAnswerRef = useRef(null)
  const summaryScrollRef = useRef(null)

  // Fetch available documents and storage stats on mount
  useEffect(() => {
    fetchAvailableDocs()
    fetchStorageStats()
  }, [])

  // Auto-scroll to bottom when conversation history updates
  useEffect(() => {
    if (conversationHistory.length > 0 && summaryScrollRef.current) {
      setTimeout(() => {
        summaryScrollRef.current.scrollTo({
          top: summaryScrollRef.current.scrollHeight,
          behavior: 'smooth'
        })
      }, 100)
    }
  }, [conversationHistory])

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
    console.log('📤 Starting file upload:', e.target.files[0].name)
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
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (progressEvent) => {
          const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          setUploadProgress({ percent, status: 'Uploading...' })
        }
      })

      console.log('✅ Upload response:', response.data)
      setUploadProgress({ percent: 100, status: 'Processing...' })

      // Go directly to generating summary (skip 'ready' state)
      setUploadProgress('generating_summary')

      // Fetch AI-generated summary
      setTimeout(async () => {
        try {
          const summaryResponse = await axios.get(`${API_URL}/api/v1/documents/${response.data.document_id}/summary`)
          
          // Check if we got valid health indicators
          const hasHealthData = summaryResponse.data.health_indicators && 
                                summaryResponse.data.health_indicators.length > 0
          
          if (!hasHealthData) {
            // No medical data found - show error
            setUploadedDoc({
              id: response.data.document_id,
              filename: response.data.filename,
              pages: summaryResponse.data.pages,
              chunks: summaryResponse.data.chunks
            })
            setUploadProgress(null)
            setError("Couldn't find any medical analysis in this document. Please try uploading a different medical report with health metrics like blood tests, vitals, or lab results.")
            setLoading(false)
            return
          }
          
          const summary = {
            title: summaryResponse.data.title,
            pages: summaryResponse.data.pages,
            chunks: summaryResponse.data.chunks,
            reportType: summaryResponse.data.report_type,
            reportDescription: summaryResponse.data.report_description,
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
          
          console.log('📊 Summary API Response:', summaryResponse.data)
          console.log('📋 Processed Summary Object:', summary)
          console.log('🔍 keyPoints:', summary.keyPoints)
          console.log('🔍 keyPoints[0]:', summary.keyPoints ? summary.keyPoints[0] : 'undefined')
          console.log('🔍 keyPoints type:', typeof summary.keyPoints)
          console.log('🔍 keyPoints is array:', Array.isArray(summary.keyPoints))
          
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
      const isFirstQuestion = conversationHistory.length === 0
      setConversationHistory(prev => [...prev, {
        question: currentQuery,
        answer: response.data.answer,
        citations: response.data.citations || [],
        confidence: response.data.confidence,
        timestamp: new Date().toISOString()
      }])
      
      setResult(response.data)
      setQuery('') // Clear input after successful query
      
      // Scroll to the latest answer after each Q&A so user sees the response
      setTimeout(() => {
        if (latestAnswerRef.current) {
          latestAnswerRef.current.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'end'
          })
        }
      }, 100)
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
    // Keep summary visible, just enable Q&A mode
    setShowSummary(false)
    
    // Scroll to Q&A section after a brief delay to ensure DOM is updated
    setTimeout(() => {
      if (qaInputRef.current) {
        qaInputRef.current.scrollIntoView({ 
          behavior: 'smooth', 
          block: 'center'
        })
        // Focus the input for better UX
        const input = qaInputRef.current.querySelector('input')
        if (input) input.focus()
      }
    }, 200)
  }

  const examples = [
    "What are my key findings?",
    "Are my results normal?",
    "What should I be concerned about?"
  ]

  return (
    <div className="mobile-full-width" style={{ minHeight: '100vh', padding: 'clamp(12px, 3vw, 20px)', maxWidth: '1200px', margin: '0 auto' }}>
      {/* Header */}
      <header className="mobile-padding-sm" style={{ marginBottom: '30px', textAlign: 'center' }}>
        <h1 className="mobile-text-lg" style={{ fontSize: '28px', fontWeight: '700', marginBottom: '8px', color: '#111827' }}>
          🏥 MediQuery AI
        </h1>
        <p className="mobile-text-sm" style={{ color: '#666', fontSize: '14px' }}>
          AI-Powered Medical Report Analysis
        </p>
        {/* Debug button hidden - uncomment to enable debug panel
        <button
          onClick={() => setShowDebug(!showDebug)}
          className="mobile-text-sm"
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
        */}
      </header>

      {/* Main Content */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: showDebug ? 'repeat(auto-fit, minmax(300px, 1fr))' : '1fr', 
        gap: 'clamp(12px, 3vw, 20px)' 
      }}>

        {/* LEFT COLUMN — Upload / Summary / Query */}
        <div>
          {!uploadedDoc ? (
            /* UPLOAD STATE */
            <div className="mobile-full-width" style={{ maxWidth: '600px', margin: '0 auto' }}>
              <div className="card" style={{ textAlign: 'center', padding: 'clamp(24px, 5vw, 40px)' }}>
                <div style={{ fontSize: 'clamp(36px, 8vw, 48px)', marginBottom: '16px' }}>🏥</div>
                <h2 style={{ fontSize: 'clamp(20px, 4vw, 24px)', fontWeight: '600', marginBottom: '12px', color: '#111827' }}>
                  AI-Powered Medical Report Analysis
                </h2>
                <p style={{ color: '#6b7280', marginBottom: '20px', fontSize: '14px', lineHeight: '1.6', maxWidth: '500px', margin: '0 auto 24px' }}>
                  Upload your medical report and ask questions in plain language. 
                  Get instant insights powered by AI.
                </p>
                
                {/* Features */}
                <div style={{ 
                  display: 'grid', 
                  gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', 
                  gap: '12px', 
                  marginBottom: '24px',
                  textAlign: 'left'
                }}>
                  <div style={{ padding: '12px', background: '#eff6ff', borderRadius: '8px' }}>
                    <div style={{ fontSize: '20px', marginBottom: '4px' }}>🔍</div>
                    <div style={{ fontSize: '12px', fontWeight: '600', color: '#1e40af' }}>Smart Analysis</div>
                  </div>
                  <div style={{ padding: '12px', background: '#f0fdf4', borderRadius: '8px' }}>
                    <div style={{ fontSize: '20px', marginBottom: '4px' }}>�</div>
                    <div style={{ fontSize: '12px', fontWeight: '600', color: '#166534' }}>Ask Questions</div>
                  </div>
                  <div style={{ padding: '12px', background: '#fef3c7', borderRadius: '8px' }}>
                    <div style={{ fontSize: '20px', marginBottom: '4px' }}>📊</div>
                    <div style={{ fontSize: '12px', fontWeight: '600', color: '#92400e' }}>Health Insights</div>
                  </div>
                </div>

                <input
                  type="file"
                  accept=".pdf"
                  onChange={handleUpload}
                  disabled={loading}
                  style={{ display: 'none' }}
                  id="file-upload"
                />

                {!loading && (
                  <label
                    htmlFor="file-upload"
                    className="mobile-text-sm"
                    style={{
                      display: 'inline-block',
                      padding: '12px 32px',
                      background: '#0284c7',
                      color: 'white',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      fontSize: '16px',
                      fontWeight: '500'
                    }}
                  >
                    📤 Choose PDF File
                  </label>
                )}

                {/* Large Circular Loading Spinner */}
                {loading && (
                  <div style={{
                    marginTop: '32px',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    gap: '20px'
                  }}>
                    <div style={{
                      width: '80px',
                      height: '80px',
                      border: '6px solid #e5e7eb',
                      borderTop: '6px solid #3b82f6',
                      borderRadius: '50%',
                      animation: 'spin 1s linear infinite'
                    }} />
                    <div style={{
                      fontSize: '18px',
                      fontWeight: '600',
                      color: '#1e40af'
                    }}>
                      Processing your report...
                    </div>
                  </div>
                )}

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
                          background: ['analyzing', 'generating_summary'].includes(uploadProgress) ? '#3b82f6' :
                            uploadProgress === 'ready' ? '#10b981' : '#e5e7eb',
                          color: ['analyzing', 'generating_summary'].includes(uploadProgress) || uploadProgress === 'ready' ? 'white' : '#9ca3af',
                          display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '12px'
                        }}>
                          {['analyzing', 'generating_summary'].includes(uploadProgress) ? '⏳' :
                            uploadProgress === 'ready' ? '✓' : '○'}
                        </div>
                        <span style={{
                          fontSize: '14px',
                          color: ['analyzing', 'generating_summary'].includes(uploadProgress) ? '#1e40af' :
                            uploadProgress === 'ready' ? '#6b7280' : '#9ca3af'
                        }}>
                          Analyzing Report
                        </span>
                      </div>

                      {/* Generating Summary */}
                      {uploadProgress === 'generating_summary' && (
                        <div style={{
                          marginTop: '16px',
                          padding: '16px',
                          background: '#dbeafe',
                          border: '1px solid #3b82f6',
                          borderRadius: '8px',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '12px'
                        }}>
                          <div className="spinner" style={{
                            width: '20px',
                            height: '20px',
                            border: '3px solid #bfdbfe',
                            borderTop: '3px solid #3b82f6',
                            borderRadius: '50%',
                            animation: 'spin 1s linear infinite'
                          }} />
                          <div style={{ fontSize: '14px', fontWeight: '600', color: '#1e40af' }}>
                            Generating AI Summary...
                          </div>
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

                <div style={{ marginTop: '24px', padding: '12px', background: '#f9fafb', borderRadius: '8px' }}>
                  <div style={{ fontSize: '12px', color: '#6b7280', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '16px', flexWrap: 'wrap' }}>
                    <span>✅ PDF files only</span>
                    <span>📏 Max 10MB</span>
                    <span>🔒 Secure & Private</span>
                  </div>
                </div>
              </div>
            </div>

          ) : uploadedDoc && !docSummary && error ? (
            /* ERROR STATE - No Medical Data Found */
            <div className="mobile-full-width" style={{ 
              maxWidth: '700px', 
              margin: '0 auto',
              padding: '0 8px'
            }}>
              <div className="card" style={{ padding: '48px 32px', textAlign: 'center' }}>
                {/* Error Icon */}
                <div style={{ fontSize: '64px', marginBottom: '24px' }}>📄</div>
                
                {/* Error Title */}
                <h3 style={{ 
                  fontSize: '20px', 
                  fontWeight: '600', 
                  color: '#111827',
                  marginBottom: '12px'
                }}>
                  No Health Metrics Found
                </h3>
                
                {/* Error Message */}
                <p style={{ 
                  fontSize: '14px', 
                  color: '#6b7280', 
                  lineHeight: '1.6',
                  marginBottom: '24px',
                  maxWidth: '500px',
                  margin: '0 auto 24px'
                }}>
                  This document doesn't contain standard health indicators like blood pressure, glucose, cholesterol, etc.
                </p>
                
                {/* Yellow Warning Box */}
                <div style={{
                  background: '#fef3c7',
                  border: '1px solid #fbbf24',
                  borderRadius: '8px',
                  padding: '16px',
                  marginBottom: '24px',
                  textAlign: 'left'
                }}>
                  <div style={{ display: 'flex', gap: '12px', alignItems: 'start' }}>
                    <div style={{ fontSize: '20px' }}>⚠️</div>
                    <div>
                      <div style={{ fontSize: '13px', fontWeight: '600', color: '#92400e', marginBottom: '4px' }}>
                        Document Status: Analysis Available
                      </div>
                      <div style={{ fontSize: '12px', color: '#78350f', lineHeight: '1.5' }}>
                        {error}
                      </div>
                    </div>
                  </div>
                </div>
                
                {/* Action Buttons */}
                <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', flexWrap: 'wrap' }}>
                  <button
                    onClick={handleClearDocument}
                    style={{
                      padding: '12px 24px',
                      background: '#3b82f6',
                      color: 'white',
                      border: 'none',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      fontSize: '14px',
                      fontWeight: '500',
                      transition: 'all 0.2s'
                    }}
                    onMouseOver={(e) => { e.target.style.background = '#2563eb'; }}
                    onMouseOut={(e) => { e.target.style.background = '#3b82f6'; }}
                  >
                    📤 Upload Different Report
                  </button>
                </div>
              </div>
            </div>

          ) : uploadedDoc && docSummary ? (
            /* SUMMARY + Q&A STATE - Combined Layout */
            <div className="mobile-full-width" style={{ 
              maxWidth: '900px', 
              margin: '0 auto',
              padding: '0 8px',
              display: 'flex',
              flexDirection: 'column',
              height: 'calc(100vh - 200px)'
            }}>
              {/* Scrollable Content Area - Summary + Q&A */}
              <div 
                ref={summaryScrollRef}
                style={{
                  flex: 1,
                  overflowY: 'auto',
                  marginBottom: '16px',
                  paddingRight: '8px'
                }}>
                <div className="card" style={{ padding: '32px' }}>
                  {/* Header */}
                  <div style={{ textAlign: 'center', marginBottom: '32px' }}>
                    <div style={{ fontSize: '48px', marginBottom: '12px' }}>✅</div>
                    <h2 style={{ fontSize: '22px', fontWeight: '600', marginBottom: '6px', color: '#111827' }}>
                      {docSummary.reportType || 'Document Processed Successfully!'}
                    </h2>
                    {docSummary.reportDescription && (
                      <p style={{ color: '#6b7280', fontSize: '14px', marginBottom: '8px', lineHeight: '1.5' }}>
                        {docSummary.reportDescription}
                      </p>
                    )}
                    <p style={{ color: '#9ca3af', fontSize: '13px' }}>📄 {docSummary.title}</p>
                  </div>

                  {/* Overall Health Score - Circular Progress */}
                  <div style={{
                    display: 'flex',
                    justifyContent: 'center',
                    marginBottom: '24px'
                  }}>
                    <div style={{
                      position: 'relative',
                      width: '160px',
                      height: '160px'
                    }}>
                      {/* Circular Progress SVG */}
                      <svg width="160" height="160" style={{ transform: 'rotate(-90deg)' }}>
                        {/* Background circle */}
                        <circle
                          cx="80"
                          cy="80"
                          r="70"
                          fill="none"
                          stroke="#e5e7eb"
                          strokeWidth="12"
                        />
                        {/* Progress circle */}
                        <circle
                          cx="80"
                          cy="80"
                          r="70"
                          fill="none"
                          stroke={docSummary.overallColor || '#10b981'}
                          strokeWidth="12"
                          strokeLinecap="round"
                          strokeDasharray={`${2 * Math.PI * 70}`}
                          strokeDashoffset={`${2 * Math.PI * 70 * (1 - 0.75)}`}
                          style={{ transition: 'stroke-dashoffset 1s ease-out' }}
                        />
                      </svg>
                      {/* Center text */}
                      <div style={{
                        position: 'absolute',
                        top: '50%',
                        left: '50%',
                        transform: 'translate(-50%, -50%)',
                        textAlign: 'center'
                      }}>
                        <div style={{ fontSize: '28px', fontWeight: '700', color: docSummary.overallColor || '#10b981' }}>
                          {docSummary.overallScore || 'N/A'}
                        </div>
                        <div style={{ fontSize: '11px', color: '#6b7280', marginTop: '4px' }}>
                          Overall Score
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Health Status Insight Box */}
                  <div style={{
                    padding: '20px',
                    background: docSummary.overallScore === 'Good' ? '#ecfdf5' : 
                               docSummary.overallScore === 'Moderate' ? '#fef3c7' : '#fee2e2',
                    border: `1px solid ${docSummary.overallScore === 'Good' ? '#10b981' : 
                                         docSummary.overallScore === 'Moderate' ? '#f59e0b' : '#ef4444'}`,
                    borderRadius: '8px',
                    marginBottom: '24px'
                  }}>
                    <div style={{ display: 'flex', gap: '12px', alignItems: 'start' }}>
                      <div style={{ fontSize: '24px' }}>
                        {docSummary.overallScore === 'Good' ? '✅' : 
                         docSummary.overallScore === 'Moderate' ? '⚠️' : '🔴'}
                      </div>
                      <div style={{ flex: 1 }}>
                        <h4 style={{ 
                          fontSize: '15px', 
                          fontWeight: '600', 
                          marginBottom: '8px',
                          color: docSummary.overallScore === 'Good' ? '#065f46' : 
                                 docSummary.overallScore === 'Moderate' ? '#92400e' : '#991b1b'
                        }}>
                          {docSummary.overallScore === 'Good' ? 'Excellent Health Status' : 
                           docSummary.overallScore === 'Moderate' ? 'Moderate Health Status - Attention Needed' : 
                           'Health Concerns Detected'}
                        </h4>
                        <p style={{ 
                          fontSize: '13px', 
                          lineHeight: '1.6',
                          color: docSummary.overallScore === 'Good' ? '#047857' : 
                                 docSummary.overallScore === 'Moderate' ? '#78350f' : '#7f1d1d'
                        }}>
                          {docSummary.overallScore === 'Good' ? 
                            'Your test results show all health indicators are within normal ranges. Continue maintaining your healthy lifestyle with regular exercise, balanced diet, and routine check-ups.' : 
                           docSummary.overallScore === 'Moderate' ? 
                            'Some of your health indicators are outside the optimal range. While not critical, these values suggest areas that may benefit from lifestyle adjustments or medical consultation. Review the specific indicators below and consider discussing them with your healthcare provider.' : 
                            'Several health indicators require attention. Please consult with your healthcare provider to discuss these results and develop an appropriate treatment or management plan.'}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Test Results Analysis - Display categorized text from multi-agent RAG */}
                  {docSummary.keyPoints?.[0] && (
                    <div style={{
                      padding: '24px',
                      background: '#ffffff',
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px',
                      marginBottom: '20px'
                    }}>
                      <div style={{
                        fontSize: '14px',
                        lineHeight: '1.8',
                        color: '#374151',
                        whiteSpace: 'pre-wrap',
                        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
                      }}>
                        {docSummary.keyPoints[0]}
                      </div>
                    </div>
                  )}

                  {/* Key Findings - Compact */}
                  {docSummary.keyPoints && docSummary.keyPoints.length > 0 && (
                    <div style={{
                      padding: '20px',
                      background: '#eff6ff',
                      border: '1px solid #bfdbfe',
                      borderRadius: '8px',
                      marginBottom: '16px'
                    }}>
                      <h4 style={{ fontSize: '14px', fontWeight: '600', marginBottom: '12px', color: '#1e40af' }}>
                        🔍 Key Findings
                      </h4>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        {docSummary.keyPoints.slice(0, 4).map((point, i) => (
                          <div key={i} style={{
                            display: 'flex',
                            alignItems: 'start',
                            gap: '10px',
                            fontSize: '13px',
                            color: '#1e40af',
                            lineHeight: '1.5'
                          }}>
                            <span style={{ fontWeight: '700', minWidth: '20px' }}>•</span>
                            <span>{point}</span>
                          </div>
                        ))}
                        {docSummary.keyPoints.length > 4 && (
                          <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '4px', fontStyle: 'italic' }}>
                            +{docSummary.keyPoints.length - 4} more findings...
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Document Metadata - Compact */}
                  <div style={{
                    fontSize: '11px',
                    color: '#9ca3af',
                    padding: '12px',
                    background: '#f9fafb',
                    borderRadius: '6px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    flexWrap: 'wrap',
                    gap: '8px'
                  }}>
                    <span>📄 {uploadedDoc?.pages || 0} pages • {uploadedDoc?.chunks || 0} chunks</span>
                    <span>🤖 {docSummary.stats.modelUsed}</span>
                  </div>
                </div>

                {/* Q&A Section - Shows after clicking Start Asking Questions */}
                {!showSummary && (
                  <div ref={qaConversationRef} className="card" style={{ padding: '24px', marginTop: '24px' }}>
                    <div style={{ 
                      marginBottom: '20px',
                      paddingBottom: '16px',
                      borderBottom: '2px solid #e5e7eb'
                    }}>
                      <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', margin: 0 }}>
                        💬 Ask Questions
                      </h3>
                    </div>

                    {/* Conversation History */}
                    {conversationHistory.length > 0 && (
                      <div style={{ marginBottom: '20px' }}>
                        {conversationHistory.map((item, idx) => (
                          <div key={idx} style={{ marginBottom: '24px' }}>
                            {/* Question */}
                            <div style={{
                              padding: '12px 16px',
                              background: '#eff6ff',
                              borderLeft: '4px solid #3b82f6',
                              borderRadius: '6px',
                              marginBottom: '12px'
                            }}>
                              <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px' }}>You asked:</div>
                              <div style={{ fontSize: '14px', color: '#1e40af', fontWeight: '500' }}>{item.question}</div>
                            </div>

                            {/* Answer */}
                            <div style={{
                              padding: '16px',
                              background: '#f9fafb',
                              border: '1px solid #e5e7eb',
                              borderRadius: '6px'
                            }}>
                              <div style={{ fontSize: '14px', color: '#374151', lineHeight: '1.6', whiteSpace: 'pre-wrap' }}>
                                {item.answer}
                              </div>
                              {item.citations && item.citations.length > 0 && (
                                <div style={{ marginTop: '12px', paddingTop: '12px', borderTop: '1px solid #e5e7eb' }}>
                                  <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '8px' }}>📚 Sources:</div>
                                  {item.citations
                                    .filter(c => {
                                      if (!c.text || !c.text.trim()) return false
                                      const text = c.text.trim()
                                      // Filter out short fragments, headers, metadata
                                      if (text.length < 30) return false
                                      // Filter out common metadata patterns
                                      if (/^(Sample Collection|Registered on|Collected on|Reported on|PID|Sex|Age|Ref\. By)/i.test(text)) return false
                                      if (/^\d+\s*-\s*\d+\s*%/.test(text)) return false  // Range patterns like "50 - 62 %"
                                      if (/^[A-Z]{2,}\s+\d/.test(text)) return false  // Abbreviations like "MCHC 32.8"
                                      return true
                                    })
                                    .slice(0, 3)  // Limit to top 3 relevant citations
                                    .map((citation, i) => (
                                      <div key={i} style={{
                                        fontSize: '12px',
                                        color: '#6b7280',
                                        marginBottom: '8px',
                                        paddingLeft: '8px',
                                        lineHeight: '1.5'
                                      }}>
                                        • <strong>Page {citation.page}:</strong> {citation.text.trim().substring(0, 200)}{citation.text.length > 200 ? '...' : ''}
                                      </div>
                                    ))}
                                </div>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}

                    {conversationHistory.length === 0 && (
                      <div style={{ textAlign: 'center', padding: '40px 20px', color: '#9ca3af' }}>
                        <div style={{ fontSize: '48px', marginBottom: '12px' }}>💬</div>
                        <div style={{ fontSize: '14px' }}>Ask your first question about the report below</div>
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Fixed Action/Input Area at Bottom */}
              <div className="card mobile-padding-sm" style={{
                padding: '20px',
                background: 'white',
                borderTop: '2px solid #e5e7eb',
                flexShrink: 0
              }}>
                {showSummary ? (
                  /* Show Start Button when summary is visible */
                  <div className="mobile-stack" style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
                    <button
                      onClick={handleProceedToQuery}
                      className="mobile-full-width"
                      style={{
                        padding: '14px 40px',
                        background: 'linear-gradient(135deg, #0284c7, #0369a1)',
                        color: 'white',
                        border: 'none',
                        borderRadius: '8px',
                        cursor: 'pointer',
                        fontSize: 'clamp(14px, 3vw, 16px)',
                        fontWeight: '600',
                        boxShadow: '0 4px 6px rgba(2, 132, 199, 0.3)',
                        transition: 'all 0.2s'
                      }}
                      onMouseOver={(e) => e.target.style.transform = 'translateY(-2px)'}
                      onMouseOut={(e) => e.target.style.transform = 'translateY(0)'}
                    >
                      🚀 Start Asking Questions
                    </button>
                    <button
                      onClick={handleClearDocument}
                      className="mobile-full-width"
                      style={{
                        padding: '14px 24px',
                        background: '#f3f4f6',
                        color: '#374151',
                        border: '1px solid #d1d5db',
                        borderRadius: '8px',
                        cursor: 'pointer',
                        fontSize: 'clamp(13px, 3vw, 14px)',
                        fontWeight: '500',
                        transition: 'all 0.2s'
                      }}
                      onMouseOver={(e) => { e.target.style.background = '#e5e7eb'; }}
                      onMouseOut={(e) => { e.target.style.background = '#f3f4f6'; }}
                    >
                      ✕ Upload Different PDF
                    </button>
                  </div>
                ) : (
                  /* Show Q&A Input when in question mode */
                  <div ref={qaInputRef}>
                    <div className="mobile-stack" style={{ display: 'flex', gap: '12px', marginBottom: '12px' }}>
                      <input
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && !loading && query.trim() && handleQuery()}
                        placeholder="Ask about your medical report..."
                        className="mobile-full-width mobile-text-sm"
                        style={{
                          flex: 1,
                          padding: '12px 16px',
                          border: '2px solid #e5e7eb',
                          borderRadius: '8px',
                          fontSize: '14px',
                          outline: 'none'
                        }}
                      />
                      <button
                        onClick={handleQuery}
                        disabled={loading || !query.trim()}
                        style={{
                          padding: '12px 24px',
                          background: loading || !query.trim() ? '#d1d5db' : '#0284c7',
                          color: 'white',
                          border: 'none',
                          borderRadius: '8px',
                          cursor: loading || !query.trim() ? 'not-allowed' : 'pointer',
                          fontSize: 'clamp(14px, 3vw, 16px)',
                          fontWeight: '500',
                          whiteSpace: 'nowrap'
                        }}
                      >
                        {loading ? '🔄' : '🚀'}
                      </button>
                    </div>
                    
                    {/* Quick Examples */}
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '16px' }}>
                      <span style={{ fontSize: '11px', color: '#9ca3af', alignSelf: 'center' }}>Quick:</span>
                      {examples.map((ex, i) => (
                        <button
                          key={i}
                          type="button"
                          onClick={() => setQuery(ex)}
                          style={{
                            padding: '4px 8px',
                            fontSize: '11px',
                            background: '#f3f4f6',
                            border: '1px solid #e5e7eb',
                            borderRadius: '4px',
                            cursor: 'pointer',
                            color: '#6b7280'
                          }}
                        >
                          {ex}
                        </button>
                      ))}
                    </div>
                    
                    {/* Clear & Upload New Button - At bottom for easy access */}
                    <div style={{ display: 'flex', justifyContent: 'center', paddingTop: '16px', borderTop: '1px solid #e5e7eb' }}>
                      <button
                        type="button"
                        onClick={handleClearDocument}
                        style={{
                          padding: '10px 20px',
                          background: '#dc2626',
                          color: 'white',
                          border: 'none',
                          borderRadius: '8px',
                          cursor: 'pointer',
                          fontSize: '14px',
                          fontWeight: '500',
                          transition: 'all 0.2s'
                        }}
                        onMouseOver={(e) => { e.target.style.background = '#b91c1c'; }}
                        onMouseOut={(e) => { e.target.style.background = '#dc2626'; }}
                      >
                        ✕ Clear & Upload New
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>

          ) : (
            /* QUERY STATE - Chat Interface */
            <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 180px)' }}>
              {/* Document Info Card - Fixed at top */}
              <div className="card" style={{ marginBottom: '16px', background: '#f0fdf4', border: '1px solid #bbf7d0', flexShrink: 0 }}>
                <div>
                  <div style={{ fontSize: '14px', fontWeight: '600', color: '#166534', marginBottom: '8px' }}>
                    ✅ Document Ready
                  </div>
                  <div style={{ fontSize: '13px', color: '#15803d' }}>
                    📄 {uploadedDoc.filename}<br />
                    📊 {uploadedDoc.pages} pages • {uploadedDoc.chunks} chunks
                  </div>
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
                      <div 
                        key={idx}
                        ref={idx === conversationHistory.length - 1 ? latestAnswerRef : null}
                      >
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
                  </div>

                  <div style={{ display: 'flex', gap: '8px' }}>
                    <input
                      type="text"
                      value={query}
                      onChange={(e) => setQuery(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && !loading && query.trim() && handleQuery()}
                      placeholder="Ask about your medical report..."
                      style={{
                        flex: 1,
                        padding: '12px 16px',
                        border: '2px solid #e5e7eb',
                        borderRadius: '8px',
                        fontSize: '14px',
                        outline: 'none'
                      }}
                    />
                    <button
                      onClick={handleQuery}
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
                      {loading ? '🔄' : '🚀'}
                    </button>
                  </div>

                  {error && (
                    <div style={{
                      padding: '10px 12px',
                      background: '#fef2f2',
                      border: '1px solid #fecaca',
                      borderRadius: '6px',
                      color: '#991b1b',
                      fontSize: '13px',
                      marginTop: '12px'
                    }}>
                      ❌ {error}
                    </div>
                  )}
                  
                  {/* Clear & Upload New Button - At bottom for easy access */}
                  <div style={{ display: 'flex', justifyContent: 'center', paddingTop: '16px', marginTop: '16px', borderTop: '1px solid #e5e7eb' }}>
                    <button
                      type="button"
                      onClick={handleClearDocument}
                      style={{
                        padding: '10px 20px',
                        background: '#dc2626',
                        color: 'white',
                        border: 'none',
                        borderRadius: '8px',
                        cursor: 'pointer',
                        fontSize: '14px',
                        fontWeight: '500',
                        transition: 'all 0.2s'
                      }}
                      onMouseOver={(e) => { e.target.style.background = '#b91c1c'; }}
                      onMouseOut={(e) => { e.target.style.background = '#dc2626'; }}
                    >
                      ✕ Clear & Upload New
                    </button>
                  </div>
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
        padding: '20px', marginTop: '40px',
        borderTop: '1px solid #e5e7eb', textAlign: 'center',
        fontSize: '12px', color: '#999'
      }}>
        <p>MediQuery AI • Healthcare Document Analysis Platform</p>
        <p style={{ marginTop: '4px' }}>Backend: FastAPI + AWS Bedrock + OpenSearch + LangGraph</p>
      </footer>
    </div>
  )
}

export default App
