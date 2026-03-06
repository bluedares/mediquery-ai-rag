import { MessageSquare, BookOpen, TrendingUp } from 'lucide-react'

export default function AnswerDisplay({ result }) {
  if (!result) return null

  return (
    <div className="card">
      <div className="flex items-center space-x-2 mb-4">
        <MessageSquare className="w-5 h-5 text-primary-600" />
        <h2 className="text-xl font-semibold text-gray-900">Answer</h2>
      </div>

      {/* Answer Text */}
      <div className="prose max-w-none mb-6">
        <div className="p-4 bg-blue-50 border-l-4 border-primary-600 rounded-r-lg">
          <p className="text-gray-800 whitespace-pre-wrap leading-relaxed">
            {result.answer}
          </p>
        </div>
      </div>

      {/* Metadata */}
      <div className="flex items-center justify-between mb-6 p-3 bg-gray-50 rounded-lg">
        <div className="flex items-center space-x-4 text-sm">
          <div className="flex items-center space-x-1">
            <TrendingUp className="w-4 h-4 text-gray-500" />
            <span className="text-gray-600">Confidence:</span>
            <span className="font-semibold text-gray-900">
              {(result.confidence * 100).toFixed(0)}%
            </span>
          </div>
          <div className="text-gray-400">•</div>
          <div className="text-gray-600">
            {result.citations?.length || 0} citations
          </div>
        </div>
        <div className="text-xs text-gray-500">
          Request ID: {result.request_id?.slice(0, 8)}...
        </div>
      </div>

      {/* Citations */}
      {result.citations && result.citations.length > 0 && (
        <div>
          <div className="flex items-center space-x-2 mb-3">
            <BookOpen className="w-4 h-4 text-gray-600" />
            <h3 className="text-sm font-semibold text-gray-900">Sources & Citations</h3>
          </div>
          
          <div className="space-y-3">
            {result.citations.map((citation, idx) => (
              <div 
                key={idx}
                className="p-4 bg-gray-50 border border-gray-200 rounded-lg hover:border-primary-300 transition-colors"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <span className="px-2 py-0.5 bg-primary-100 text-primary-700 text-xs font-medium rounded">
                      Source {idx + 1}
                    </span>
                    <span className="text-xs text-gray-500">
                      Page {citation.page}
                      {citation.section && ` • ${citation.section}`}
                    </span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <div className="w-16 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-primary-600 h-2 rounded-full"
                        style={{ width: `${citation.relevance_score * 100}%` }}
                      />
                    </div>
                    <span className="text-xs text-gray-600">
                      {(citation.relevance_score * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
                <p className="text-sm text-gray-700 leading-relaxed">
                  {citation.text}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
