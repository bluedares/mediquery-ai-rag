#!/bin/bash

# MediQuery AI - Deployment Script
# Supports: AWS Lambda, Docker, Local

set -e

echo "=================================="
echo "🚀 MediQuery AI Deployment"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Deployment mode
MODE=${1:-local}

case $MODE in
  lambda)
    echo -e "${BLUE}📦 Deploying to AWS Lambda...${NC}"
    echo ""
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        echo -e "${YELLOW}⚠️  AWS CLI not found. Installing...${NC}"
        brew install awscli
    fi
    
    # Check SAM CLI
    if ! command -v sam &> /dev/null; then
        echo -e "${YELLOW}⚠️  SAM CLI not found. Installing...${NC}"
        brew tap aws/tap
        brew install aws-sam-cli
    fi
    
    # Add mangum to requirements
    if ! grep -q "mangum" backend/requirements.txt; then
        echo "mangum>=0.17.0" >> backend/requirements.txt
    fi
    
    cd backend
    
    # Build
    echo -e "${BLUE}🔨 Building SAM application...${NC}"
    sam build
    
    # Deploy
    echo -e "${BLUE}🚀 Deploying to AWS...${NC}"
    sam deploy --guided
    
    echo ""
    echo -e "${GREEN}✅ Lambda deployment complete!${NC}"
    echo "Check AWS Console for API Gateway URL"
    ;;
    
  docker)
    echo -e "${BLUE}🐳 Building Docker image...${NC}"
    echo ""
    
    cd backend
    
    # Build image
    docker build -f Dockerfile.lambda -t mediquery-api:latest .
    
    echo ""
    echo -e "${GREEN}✅ Docker image built!${NC}"
    echo ""
    echo "To run locally:"
    echo "  docker run -p 8000:8080 mediquery-api:latest"
    echo ""
    echo "To push to ECR:"
    echo "  aws ecr create-repository --repository-name mediquery-api"
    echo "  docker tag mediquery-api:latest <account>.dkr.ecr.us-east-1.amazonaws.com/mediquery-api:latest"
    echo "  docker push <account>.dkr.ecr.us-east-1.amazonaws.com/mediquery-api:latest"
    ;;
    
  local)
    echo -e "${BLUE}💻 Starting local development servers...${NC}"
    echo ""
    
    # Start backend
    echo -e "${BLUE}Starting backend on port 8000...${NC}"
    cd backend
    python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    
    # Wait for backend
    sleep 3
    
    # Start frontend
    echo -e "${BLUE}Starting frontend on port 5173...${NC}"
    cd ../frontend
    npm run dev &
    FRONTEND_PID=$!
    
    echo ""
    echo -e "${GREEN}✅ Local servers started!${NC}"
    echo ""
    echo "Backend:  http://localhost:8000"
    echo "Frontend: http://localhost:5173"
    echo "API Docs: http://localhost:8000/docs"
    echo ""
    echo "Press Ctrl+C to stop servers"
    
    # Wait for interrupt
    trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
    wait
    ;;
    
  *)
    echo "Usage: ./deploy.sh [local|lambda|docker]"
    echo ""
    echo "Modes:"
    echo "  local   - Start local development servers (default)"
    echo "  lambda  - Deploy to AWS Lambda with SAM"
    echo "  docker  - Build Docker image for Lambda"
    exit 1
    ;;
esac
