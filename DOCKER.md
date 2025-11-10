# Docker Deployment Guide

## Quick Start with Docker Compose

### Prerequisites
- Docker and Docker Compose installed
- Kubernetes cluster access (kubeconfig at `~/.kube/config`)
- API keys for OpenAI or LLM Farm
- Tavily API key for web search

### Step 1: Configure Environment

Copy the environment template:
```bash
cp .env.docker .env
```

Edit `.env` and add your API keys:
```bash
# For OpenAI
USE_LLM_FARM=false
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o

# For Tavily Search
TAVILY_API_KEY=tvly-...
```

### Step 2: Build and Run

Build and start all services:
```bash
docker-compose up --build
```

Or run in detached mode:
```bash
docker-compose up -d --build
```

### Step 3: Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Step 4: Stop Services

```bash
docker-compose down
```

To remove volumes as well:
```bash
docker-compose down -v
```

## Individual Service Builds

### Build Agent Backend Only
```bash
cd agent
docker build -t chat-k8s-agent .
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your-key \
  -e TAVILY_API_KEY=your-key \
  -v ~/.kube/config:/app/kubeconfig.yaml:ro \
  chat-k8s-agent
```

### Build Frontend Only
```bash
docker build -t chat-k8s-frontend .
docker run -p 3000:3000 \
  -e AGENT_URL=http://localhost:8000/ \
  chat-k8s-frontend
```

## Environment Variables

### Agent Backend (`agent/Dockerfile`)

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `USE_LLM_FARM` | Use LLM Farm instead of OpenAI | `false` | No |
| `LLM_FARM_BASE_URL` | LLM Farm API endpoint | - | If USE_LLM_FARM=true |
| `LLM_FARM_API_KEY` | LLM Farm subscription key | - | If USE_LLM_FARM=true |
| `LLM_FARM_MODEL` | Model to use | `gpt-4o` | No |
| `OPENAI_API_KEY` | OpenAI API key | - | If USE_LLM_FARM=false |
| `OPENAI_MODEL` | OpenAI model | `gpt-4o` | No |
| `TAVILY_API_KEY` | Tavily search API key | - | Yes |
| `KUBECONFIG` | Path to kubeconfig | `/app/kubeconfig.yaml` | Yes |
| `LOG_LEVEL` | Logging level | `info` | No |
| `LOGFIRE_TOKEN` | Logfire token (optional) | - | No |
| `HOST` | Server host | `0.0.0.0` | No |
| `PORT` | Server port | `8000` | No |

### Frontend (`Dockerfile`)

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `AGENT_URL` | Backend agent URL | `http://localhost:8000/` | Yes |
| `NODE_ENV` | Node environment | `production` | No |

## Kubernetes Access

The agent container needs access to your Kubernetes cluster. The docker-compose.yml mounts your kubeconfig:

```yaml
volumes:
  - ${HOME}/.kube/config:/app/kubeconfig.yaml:ro
```

**For custom kubeconfig locations:**
```bash
# Set in .env file
echo "KUBECONFIG_PATH=/path/to/your/kubeconfig" >> .env
```

Then update docker-compose.yml:
```yaml
volumes:
  - ${KUBECONFIG_PATH:-${HOME}/.kube/config}:/app/kubeconfig.yaml:ro
```

## Production Considerations

### Security
1. **Never commit `.env` files** - already in `.gitignore`
2. **Use secrets management** in production (Kubernetes Secrets, Docker Secrets, HashiCorp Vault)
3. **Limit kubeconfig permissions** - use service accounts with RBAC
4. **Enable HTTPS** - use reverse proxy (nginx, Traefik) with SSL/TLS

### Scaling
```yaml
# docker-compose.yml
services:
  frontend:
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1'
          memory: 512M
```

### Health Checks
Both services have health checks configured:
```bash
docker-compose ps  # View service health status
```

### Logging
View logs:
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f agent
docker-compose logs -f frontend

# Last 100 lines
docker-compose logs --tail=100 agent
```

Agent logs are also persisted to `./agent/logs/` directory.

### Monitoring
```bash
# Resource usage
docker stats

# Inspect services
docker-compose ps
docker inspect chat-k8s-agent
docker inspect chat-k8s-frontend
```

## Troubleshooting

### Agent fails to start
```bash
# Check logs
docker-compose logs agent

# Common issues:
# 1. Missing API keys - check .env file
# 2. Kubeconfig not found - verify ~/.kube/config exists
# 3. Port conflict - ensure 8000 is available
```

### Frontend can't connect to agent
```bash
# Verify agent is running
curl http://localhost:8000/health

# Check network
docker network inspect chat-k8s_chat-k8s-network

# Verify AGENT_URL in frontend
docker exec chat-k8s-frontend env | grep AGENT_URL
```

### Kubernetes operations fail
```bash
# Test kubeconfig mount
docker exec -it chat-k8s-agent cat /app/kubeconfig.yaml

# Test kubectl access (if installed in container)
docker exec -it chat-k8s-agent kubectl get nodes
```

### Build failures
```bash
# Clean build (no cache)
docker-compose build --no-cache

# Remove old images
docker-compose down --rmi all

# Rebuild specific service
docker-compose build agent
```

## Development vs Production

### Development (with hot-reload)
Use the npm scripts instead:
```bash
npm run dev  # Runs both frontend and agent with hot-reload
```

### Production (Docker)
Use Docker Compose for isolated, containerized deployment:
```bash
docker-compose up -d --build
```

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Build and Push Docker Images

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Agent
        run: docker build -t myregistry/chat-k8s-agent:${{ github.sha }} ./agent
      
      - name: Build Frontend
        run: docker build -t myregistry/chat-k8s-frontend:${{ github.sha }} .
      
      - name: Push Images
        run: |
          docker push myregistry/chat-k8s-agent:${{ github.sha }}
          docker push myregistry/chat-k8s-frontend:${{ github.sha }}
```

## Multi-Architecture Builds

Build for multiple platforms:
```bash
# Enable buildx
docker buildx create --use

# Build for AMD64 and ARM64
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t chat-k8s-agent:latest \
  ./agent \
  --push
```
