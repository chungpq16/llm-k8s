#!/bin/bash
set -e

echo "🚀 Chat with K8s - Quick Start Script"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  No .env file found. Creating from template...${NC}"
    cp .env.docker .env
    echo -e "${GREEN}✅ Created .env file${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  IMPORTANT: Please edit .env and add your API keys before continuing!${NC}"
    echo ""
    echo "Required keys:"
    echo "  - OPENAI_API_KEY (if using OpenAI)"
    echo "  - TAVILY_API_KEY (for web search)"
    echo "  - LLM_FARM_* (if using LLM Farm)"
    echo ""
    read -p "Press Enter after updating .env file..."
fi

# Check if kubeconfig exists
if [ ! -f ~/.kube/config ]; then
    echo -e "${RED}❌ No kubeconfig found at ~/.kube/config${NC}"
    echo "Please ensure you have Kubernetes cluster access configured."
    exit 1
fi

echo -e "${GREEN}✅ Kubeconfig found${NC}"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found. Please install Docker first.${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose not found. Please install Docker Compose first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker and Docker Compose found${NC}"
echo ""

# Build and start services
echo "🔨 Building Docker images..."
docker-compose build

echo ""
echo "🚀 Starting services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 5

# Check service health
if docker-compose ps | grep -q "healthy"; then
    echo -e "${GREEN}✅ Services are running!${NC}"
    echo ""
    echo "📍 Access your application:"
    echo "   Frontend:  http://localhost:3000"
    echo "   Backend:   http://localhost:8000"
    echo "   API Docs:  http://localhost:8000/docs"
    echo ""
    echo "📋 Useful commands:"
    echo "   View logs:    docker-compose logs -f"
    echo "   Stop:         docker-compose down"
    echo "   Restart:      docker-compose restart"
    echo "   Or use:       make help"
    echo ""
else
    echo -e "${YELLOW}⚠️  Services started but may not be fully healthy yet.${NC}"
    echo "   Check status: docker-compose ps"
    echo "   View logs:    docker-compose logs -f"
fi
