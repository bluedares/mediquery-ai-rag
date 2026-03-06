#!/bin/bash

echo "=================================="
echo "MediQuery AI - Integration Test"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Backend Health Check
echo "📋 Test 1: Backend Health Check"
HEALTH=$(curl -s http://localhost:8000/health)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Backend is running${NC}"
    echo "   Response: $(echo $HEALTH | jq -r '.status')"
else
    echo -e "${RED}❌ Backend is not responding${NC}"
    exit 1
fi
echo ""

# Test 2: Frontend Availability
echo "📋 Test 2: Frontend Availability"
FRONTEND=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5173)
if [ "$FRONTEND" = "200" ]; then
    echo -e "${GREEN}✅ Frontend is running${NC}"
else
    echo -e "${RED}❌ Frontend is not responding (HTTP $FRONTEND)${NC}"
fi
echo ""

# Test 3: API Query Endpoint
echo "📋 Test 3: API Query Endpoint"
QUERY_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the primary endpoints?",
    "document_id": "doc_test_001",
    "include_trace": true
  }')

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Query endpoint responding${NC}"
    
    # Extract key metrics
    ANSWER_LENGTH=$(echo $QUERY_RESPONSE | jq -r '.answer' | wc -c)
    CONFIDENCE=$(echo $QUERY_RESPONSE | jq -r '.confidence')
    PROCESSING_TIME=$(echo $QUERY_RESPONSE | jq -r '.processing_time_ms')
    AGENT_COUNT=$(echo $QUERY_RESPONSE | jq -r '.agent_trace | length')
    
    echo "   Answer length: $ANSWER_LENGTH chars"
    echo "   Confidence: $CONFIDENCE"
    echo "   Processing time: ${PROCESSING_TIME}ms"
    echo "   Agents executed: $AGENT_COUNT"
else
    echo -e "${RED}❌ Query endpoint failed${NC}"
fi
echo ""

# Test 4: CORS Headers
echo "📋 Test 4: CORS Configuration"
CORS=$(curl -s -I http://localhost:8000/health | grep -i "access-control-allow-origin")
if [ ! -z "$CORS" ]; then
    echo -e "${GREEN}✅ CORS headers present${NC}"
    echo "   $CORS"
else
    echo -e "${YELLOW}⚠️  CORS headers not found${NC}"
fi
echo ""

# Summary
echo "=================================="
echo "✅ Integration Test Complete"
echo "=================================="
echo ""
echo "🌐 Frontend: http://localhost:5173"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Ready for demo! 🚀"
