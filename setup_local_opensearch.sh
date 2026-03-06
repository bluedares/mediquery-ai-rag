#!/bin/bash
# Setup Local OpenSearch with Docker

echo "🚀 Setting up local OpenSearch..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Stop and remove existing container if it exists
docker stop opensearch-node 2>/dev/null
docker rm opensearch-node 2>/dev/null

# Run OpenSearch container
echo "📦 Starting OpenSearch container..."
docker run -d \
  --name opensearch-node \
  -p 9200:9200 \
  -p 9600:9600 \
  -e "discovery.type=single-node" \
  -e "OPENSEARCH_INITIAL_ADMIN_PASSWORD=Admin123!" \
  -e "DISABLE_SECURITY_PLUGIN=true" \
  opensearchproject/opensearch:2.11.0

echo "⏳ Waiting for OpenSearch to start (30 seconds)..."
sleep 30

# Test connection
echo "🧪 Testing OpenSearch connection..."
curl -s http://localhost:9200 | grep -q "opensearch" && \
  echo "✅ OpenSearch is running!" || \
  echo "❌ OpenSearch failed to start. Check: docker logs opensearch-node"

echo ""
echo "📝 Update your .env file:"
echo "OPENSEARCH_ENDPOINT=http://localhost:9200"
echo ""
echo "🔧 Useful commands:"
echo "  - View logs: docker logs -f opensearch-node"
echo "  - Stop: docker stop opensearch-node"
echo "  - Start: docker start opensearch-node"
echo "  - Remove: docker stop opensearch-node && docker rm opensearch-node"
