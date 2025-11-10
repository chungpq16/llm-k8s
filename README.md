# Chat with K8s - AI-Powered Kubernetes Assistant 🚀

An intelligent chatbot that helps you interact with Kubernetes clusters using natural language, powered by Pydantic AI, Tavily search, and Model Context Protocol (MCP) servers.

## ✨ Features

- 🤖 **Intelligent AI Agent** - Powered by Pydantic AI with GPT-4 or LLM Farm support
- 🔍 **Web Search Integration** - Real-time web search capabilities via Tavily API
- ☸️ **Kubernetes Operations** - Direct cluster interaction using MCP Kubernetes server
- 🌐 **Modern UI** - Built with Next.js and CopilotKit for seamless chat experience
- 📦 **Easy Deployment** - Docker and docker-compose ready for production
- 🔧 **LLM Farm Support** - Enterprise-ready with custom LLM endpoint support

## 🚀 Quick Start

### Option 1: Docker (Recommended for Production)

```bash
# 1. Configure environment
cp .env.docker .env
# Edit .env and add your API keys

# 2. Start services
make start
# or
docker-compose up --build

# 3. Access the application
# Frontend: http://localhost:3000
# Backend:  http://localhost:8000
```

See [DOCKER.md](DOCKER.md) for detailed Docker deployment guide.

### Option 2: Development Mode (Hot-Reload)

```bash
# 1. Install dependencies
npm install

# 2. Configure agent
cd agent
cp .env.example .env
# Edit .env and add your API keys

# 3. Return to root and start dev servers
cd ..
npm run dev

# Frontend: http://localhost:3000
# Backend:  http://localhost:8000
```

## 📋 Prerequisites

### Required
- **Node.js** 20+ and npm
- **Python** 3.12+
- **uv** package manager (for Python)
- **Kubernetes cluster access** with valid kubeconfig
- **API Keys**:
  - OpenAI API key OR LLM Farm endpoint + key
  - Tavily API key for web search

### Optional
- Docker and Docker Compose (for containerized deployment)
- kubectl CLI (for manual Kubernetes operations)

## 🔑 Configuration

### Environment Variables

#### Agent Backend (agent/.env)
```bash
# LLM Configuration
USE_LLM_FARM=false                    # Use LLM Farm (true) or OpenAI (false)

# OpenAI (if USE_LLM_FARM=false)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o

# LLM Farm (if USE_LLM_FARM=true)
LLM_FARM_BASE_URL=https://your-endpoint.com/v1
LLM_FARM_API_KEY=your-key
LLM_FARM_MODEL=gpt-4o

# Tavily Search
TAVILY_API_KEY=tvly-...

# Kubernetes
KUBECONFIG=/path/to/kubeconfig.yaml

# Logging (optional)
LOG_LEVEL=info
LOGFIRE_TOKEN=your-token
```

#### Frontend (.env.local)
```bash
AGENT_URL=http://localhost:8000/
```

## 🛠️ Development Commands

### Using Makefile
```bash
make help        # Show all available commands
make build       # Build Docker images
make up          # Start services
make down        # Stop services
make logs        # View all logs
make agent       # View agent logs
make frontend    # View frontend logs
make restart     # Restart services
make clean       # Clean up Docker resources
make dev         # Run development mode
```

### Using npm scripts
```bash
npm run dev              # Start both frontend and agent
npm run dev:debug        # Start with debug logging
npm run dev:agent        # Start agent only
npm run dev:ui           # Start frontend only
npm run build            # Build frontend for production
npm run start            # Start production frontend
npm run lint             # Lint the code
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         Next.js Frontend (3000)         │
│    CopilotKit + React Components        │
└─────────────┬───────────────────────────┘
              │ HTTP/GraphQL
              ▼
┌─────────────────────────────────────────┐
│    Pydantic AI Agent Backend (8000)     │
│  ┌──────────────────────────────────┐   │
│  │   LLM (GPT-4 / LLM Farm)         │   │
│  └──────────────────────────────────┘   │
│  ┌──────────────────────────────────┐   │
│  │   Tavily Search Tool             │   │
│  └──────────────────────────────────┘   │
│  ┌──────────────────────────────────┐   │
│  │   MCP Kubernetes Server          │   │
│  │   - Pod operations               │   │
│  │   - Deployment management        │   │
│  │   - Service discovery            │   │
│  └──────────────────────────────────┘   │
│  ┌──────────────────────────────────┐   │
│  │   MCP Fetch Server               │   │
│  │   - Web content fetching         │   │
│  └──────────────────────────────────┘   │
└─────────────┬───────────────────────────┘
              │
              ▼
      ┌───────────────┐
      │  Kubernetes   │
      │    Cluster    │
      └───────────────┘
```

## 📚 Key Technologies

- **Frontend**: Next.js 15, React 19, CopilotKit, Tailwind CSS
- **Backend**: Python 3.12, Pydantic AI, FastAPI, Uvicorn
- **AI/LLM**: OpenAI GPT-4 or LLM Farm, Tavily Search
- **Integrations**: Model Context Protocol (MCP), Kubernetes API
- **DevOps**: Docker, Docker Compose, uv package manager

## 🔍 Features Deep Dive

### AI Agent Capabilities
- Natural language understanding for Kubernetes operations
- Context-aware responses with conversation history
- Web search integration for up-to-date information
- Tool-based execution for deterministic operations

### Kubernetes Operations
Via MCP Kubernetes server:
- List and describe pods, deployments, services
- Get pod logs and events
- Execute commands in pods
- Resource status monitoring

### Web Search
- Real-time search via Tavily API
- Query optimization and result summarization
- Source citation and verification

## 🧪 Testing

```bash
# Test agent endpoint
curl http://localhost:8000/health

# Test frontend
curl http://localhost:3000/

# Test Kubernetes access
kubectl get nodes
```

## 📖 Documentation

- [Docker Deployment Guide](DOCKER.md) - Complete Docker setup and troubleshooting
- [Agent Documentation](agent/README.md) - Python backend details
- [MCP Configuration](agent/mcp_config.json) - MCP server setup

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Pydantic AI](https://ai.pydantic.dev/) - Type-safe AI agent framework
- [CopilotKit](https://copilotkit.ai/) - AI copilot integration
- [Tavily](https://tavily.com/) - AI search API
- [Model Context Protocol](https://modelcontextprotocol.io/) - Universal AI integration

## 📞 Support

For issues and questions:
- Create an issue in the repository
- Check existing issues for solutions
- Review the [DOCKER.md](DOCKER.md) troubleshooting section

## 🚦 Status

✅ Production Ready
- Multi-LLM support (OpenAI, LLM Farm)
- Docker containerization
- Health checks and monitoring
- Comprehensive logging
- Error handling and recovery

---

**Happy Kubernetes chatting! 🎉**
