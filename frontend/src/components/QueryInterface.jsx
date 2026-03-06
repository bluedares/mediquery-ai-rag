import { useState } from 'react'
import axios from 'axios'
import { Send, FileText, Loader2, CheckCircle, XCircle } from 'lucide-react'
import AnswerDisplay from './AnswerDisplay'

const API_URL = 'http://localhost:8000'

export default function QueryInterface({ onResult, loading, setLoading }) {
  const [query, setQuery] = useState('')
  const [documentId, setDocumentId] = useState('doc_sample_001')
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!query.trim()) {
      setError('Please enter a question')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await axios.post(`${API_URL}/api/v1/query`, {
        query: query.trim(),
        document_id: documentId,
        include_trace: true
      })

      setResult(response.data)
      onResult(response.data)
    } catch (err) {
      const errorMsg = err.response?.data?.detail?.message || err.message || 'Failed to process query'
      setError(errorMsg)
      console.error('Query error:', err)
    } finally {
      setLoading(false)
    }
  }

  const exampleQueries = [
    "What are the primary endpoints of this trial?",
    "What are the common side effects?",
    "What is the patient eligibility criteria?",
    "What is the dosing schedule?"
  ]

  return (
    <div>
      {/* Query Form Card */}
      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
          <FileText style={{ width: 20, height: 20, color: '#0284c7' }} />
          <h2 style={{ fontSize: '20px', fontWeight: '600', margin: 0 }}>Ask a Question</h2>
        </div>

        <form onSubmit={handleSubmit}>
          {/* Document ID */}
          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
              Document ID
            </label>
            <input
              type="text"
              value={documentId}
              onChange={(e) => setDocumentId(e.target.value)}
              className="input-field"
              placeholder="e.g., doc_sample_001"
            />
          </div>

          {/* Query Input */}
          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
              Your Question
            </label>
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="input-field"
              rows={4}
              placeholder="Ask a question about the clinical document..."
              disabled={loading}
            />
          </div>

          {/* Example Queries */}
          <div style={{ marginBottom: '16px' }}>
            <p style={{ fontSize: '12px', color: '#6b7280', marginBottom: '8px' }}>Try these examples:</p>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {exampleQueries.map((example, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => setQuery(example)}
                  style={{
                    fontSize: '12px',
                    padding: '4px 12px',
                    background: '#f3f4f6',
                    color: '#374151',
                    border: 'none',
                    borderRadius: '999px',
                    cursor: loading ? 'not-allowed' : 'pointer',
                    transition: 'background 0.2s'
                  }}
                  disabled={loading}
                  onMouseOver={(e) => !loading && (e.target.style.background = '#e5e7eb')}
                  onMouseOut={(e) => e.target.style.background = '#f3f4f6'}
                >
                  {example}
                </button>
              ))}
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="btn-primary"
            style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
          >
            {loading ? (
              <>
                <Loader2 style={{ width: 20, height: 20, animation: 'spin 1s linear infinite' }} />
                <span>Processing...</span>
              </>
            ) : (
              <>
                <Send style={{ width: 20, height: 20 }} />
                <span>Ask Question</span>
              </>
            )}
          </button>
        </form>

        {/* Error Display */}
        {error && (
          <div style={{
            marginTop: '16px',
            padding: '16px',
            background: '#fef2f2',
            border: '1px solid #fecaca',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'flex-start',
            gap: '12px'
          }}>
            <XCircle style={{ width: 20, height: 20, color: '#dc2626', flexShrink: 0, marginTop: '2px' }} />
            <div>
              <p style={{ fontSize: '14px', fontWeight: '500', color: '#991b1b', margin: 0 }}>Error</p>
              <p style={{ fontSize: '14px', color: '#b91c1c', marginTop: '4px' }}>{error}</p>
            </div>
          </div>
        )}

        {/* Success Indicator */}
        {result && !error && (
          <div style={{
            marginTop: '16px',
            padding: '16px',
            background: '#f0fdf4',
            border: '1px solid #bbf7d0',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'flex-start',
            gap: '12px'
          }}>
            <CheckCircle style={{ width: 20, height: 20, color: '#16a34a', flexShrink: 0, marginTop: '2px' }} />
            <div>
              <p style={{ fontSize: '14px', fontWeight: '500', color: '#166534', margin: 0 }}>Query Processed</p>
              <p style={{ fontSize: '14px', color: '#15803d', marginTop: '4px' }}>
                Completed in {result.processing_time_ms?.toFixed(0)}ms • 
                Confidence: {(result.confidence * 100).toFixed(0)}%
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Answer Display */}
      {result && <AnswerDisplay result={result} />}
    </div>
  )
}
