# UI Changes Implementation Plan

## 📋 Requirements from Screenshots

### 1. Query Error Issue
**Error**: "I encountered an error while generating the answer. Please try again."
**Root Cause**: Need to check backend agent_graph execution
**Fix**: Investigate agent workflow and add better error handling

### 2. Text Changes
- ✅ "Select Existing Document" → "Recent Reports"
- ✅ "Ask a Question" → Better health-report specific text
- ✅ "Your Question" → Remove redundancy

### 3. Document Summary UI
**When document selected from dropdown**:
- Show summary with health indicators
- Use progress bars or visual indicators for:
  - Good/Okay/Bad metrics
  - Overall health score
  - Key findings visualization

### 4. UI Reordering
**Current Order**:
1. Document Ready (top)
2. Ask a Question (middle)
3. Answer (bottom)

**New Order**:
1. Document Ready (top)
2. Answer (middle) ← Move up
3. Ask a Question (bottom) ← Move down

## 🎨 Implementation Details

### Change 1: Dropdown Text
```jsx
"📁 Select Existing Document" → "📊 Recent Reports"
```

### Change 2: Query Section Labels
```jsx
"📝 Ask a Question" → "💬 Ask About Your Report"
"Your Question" → "What would you like to know?"
```

### Change 3: Document Summary with Health Indicators
When a document is selected, show:
```
┌─────────────────────────────────────┐
│  📊 Report Summary                  │
│                                     │
│  📄 diabetes_study.pdf              │
│                                     │
│  Health Indicators:                 │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│  🟢 Blood Glucose    ████████░░ 80% │
│  🟡 Cholesterol      ██████░░░░ 60% │
│  🔴 Blood Pressure   ████░░░░░░ 40% │
│                                     │
│  Overall Score: 🟡 Moderate         │
└─────────────────────────────────────┘
```

### Change 4: UI Reordering
Move result section ABOVE query input section in the DOM

## 🔧 Files to Modify

1. **frontend/src/App.jsx**
   - Line ~243: Change dropdown button text
   - Line ~400-500: Reorder Answer and Query sections
   - Line ~420: Change query section labels
   - Add: Document summary component with health indicators

2. **backend/app/api/query.py**
   - Add better error handling
   - Return more detailed error messages

## 🚀 Implementation Order

1. Fix query error (check agent_graph)
2. Change text labels
3. Reorder UI sections
4. Add document summary with health indicators
5. Test complete flow
