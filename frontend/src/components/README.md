# Frontend Components

## Component Architecture

### App.jsx
Main application component that orchestrates the entire UI.

**Features:**
- Header with branding and tech badges
- Two-column layout (query interface + agent trace)
- State management for query results and loading
- Responsive design

### QueryInterface.jsx
Handles user input and API communication.

**Props:**
- `onResult`: Callback for query results
- `loading`: Loading state
- `setLoading`: Loading state setter

**Features:**
- Document ID input
- Query textarea with validation
- Example query buttons
- Submit button with loading state
- Success/error notifications
- API integration with axios

### AnswerDisplay.jsx
Displays the AI-generated answer with citations.

**Props:**
- `result`: Query result object

**Features:**
- Formatted answer text
- Confidence score display
- Citation list with relevance scores
- Source attribution (page, section)
- Request ID tracking

### AgentTrace.jsx
Visualizes the multi-agent workflow.

**Props:**
- `trace`: Array of agent execution steps
- `loading`: Loading state

**Features:**
- Timeline visualization
- Agent-specific emojis and colors
- Execution time per agent
- Success/failure indicators
- Total workflow summary
- Sticky positioning for better UX

## Data Flow

```
User Input → QueryInterface → Backend API → Response
                                              ↓
                                         onResult()
                                              ↓
                                    ┌─────────┴─────────┐
                                    ↓                   ↓
                            AnswerDisplay         AgentTrace
```

## Styling

All components use TailwindCSS utility classes with custom theme colors defined in `tailwind.config.js`.

### Custom Classes
- `.card` - White card with shadow
- `.btn-primary` - Primary action button
- `.btn-secondary` - Secondary action button
- `.input-field` - Form input styling

## API Integration

Backend endpoint: `http://localhost:8000/api/v1/query`

Request format:
```json
{
  "query": "What are the side effects?",
  "document_id": "doc_sample_001",
  "include_trace": true
}
```

Response format:
```json
{
  "request_id": "uuid",
  "answer": "The answer text...",
  "citations": [...],
  "confidence": 0.85,
  "processing_time_ms": 2500,
  "agent_trace": [...]
}
```
