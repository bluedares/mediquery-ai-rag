import { Activity, Clock, CheckCircle, XCircle, Loader2 } from 'lucide-react'

const AGENT_EMOJIS = {
  'QueryAnalyzerAgent': '🔍',
  'RetrievalAgent': '📚',
  'RerankingAgent': '🎯',
  'SynthesisAgent': '✍️'
}

const AGENT_COLORS = {
  'QueryAnalyzerAgent': 'bg-blue-100 text-blue-800 border-blue-200',
  'RetrievalAgent': 'bg-green-100 text-green-800 border-green-200',
  'RerankingAgent': 'bg-yellow-100 text-yellow-800 border-yellow-200',
  'SynthesisAgent': 'bg-purple-100 text-purple-800 border-purple-200'
}

export default function AgentTrace({ trace, loading }) {
  return (
    <div className="card sticky top-4">
      <div className="flex items-center space-x-2 mb-4">
        <Activity className="w-5 h-5 text-primary-600" />
        <h2 className="text-xl font-semibold text-gray-900">Agent Workflow</h2>
      </div>

      {loading && (
        <div className="flex flex-col items-center justify-center py-12">
          <Loader2 className="w-12 h-12 text-primary-600 animate-spin mb-4" />
          <p className="text-sm text-gray-600">Processing your query...</p>
          <p className="text-xs text-gray-500 mt-1">Multi-agent system in action</p>
        </div>
      )}

      {!loading && !trace && (
        <div className="text-center py-12">
          <Activity className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <p className="text-sm text-gray-500">Submit a query to see agent workflow</p>
        </div>
      )}

      {!loading && trace && trace.length > 0 && (
        <div className="space-y-3">
          {/* Timeline */}
          <div className="relative">
            {trace.map((step, idx) => (
              <div key={idx} className="relative pb-8 last:pb-0">
                {/* Timeline Line */}
                {idx < trace.length - 1 && (
                  <div className="absolute left-4 top-8 bottom-0 w-0.5 bg-gray-200" />
                )}

                {/* Agent Step */}
                <div className="relative flex items-start space-x-3">
                  {/* Icon */}
                  <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                    step.status === 'success' ? 'bg-green-100' : 'bg-red-100'
                  }`}>
                    {step.status === 'success' ? (
                      <CheckCircle className="w-5 h-5 text-green-600" />
                    ) : (
                      <XCircle className="w-5 h-5 text-red-600" />
                    )}
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className={`p-3 rounded-lg border ${
                      AGENT_COLORS[step.agent] || 'bg-gray-100 text-gray-800 border-gray-200'
                    }`}>
                      <div className="flex items-center justify-between mb-1">
                        <div className="flex items-center space-x-2">
                          <span className="text-lg">
                            {AGENT_EMOJIS[step.agent] || '🤖'}
                          </span>
                          <span className="text-sm font-semibold">
                            {step.agent.replace('Agent', '')}
                          </span>
                        </div>
                        <div className="flex items-center space-x-1 text-xs">
                          <Clock className="w-3 h-3" />
                          <span>{step.duration_ms?.toFixed(0)}ms</span>
                        </div>
                      </div>
                      
                      {/* Progress Bar */}
                      <div className="mt-2">
                        <div className="w-full bg-white bg-opacity-50 rounded-full h-1">
                          <div 
                            className="bg-current h-1 rounded-full transition-all duration-500"
                            style={{ width: '100%' }}
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Summary */}
          <div className="mt-4 p-3 bg-gray-50 rounded-lg border border-gray-200">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Total Steps:</span>
              <span className="font-semibold text-gray-900">{trace.length}</span>
            </div>
            <div className="flex items-center justify-between text-sm mt-2">
              <span className="text-gray-600">Total Time:</span>
              <span className="font-semibold text-gray-900">
                {trace.reduce((sum, step) => sum + (step.duration_ms || 0), 0).toFixed(0)}ms
              </span>
            </div>
            <div className="flex items-center justify-between text-sm mt-2">
              <span className="text-gray-600">Success Rate:</span>
              <span className="font-semibold text-green-600">
                {((trace.filter(s => s.status === 'success').length / trace.length) * 100).toFixed(0)}%
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
