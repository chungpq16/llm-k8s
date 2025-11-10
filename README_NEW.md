# Kubernetes AI Chatbot with Pydantic AI and AG-UI

An intelligent Kubernetes assistant powered by Pydantic AI, featuring web search capabilities, Kubernetes cluster operations, and support for LLM Farm enterprise deployments.

## 🌟 Features

- **🤖 AI-Powered Chat**: Natural language interface for Kubernetes operations
- **🔍 Web Search**: Real-time information retrieval via Tavily
- **☸️ Kubernetes Operations**: Full cluster management through MCP server
- **📦 Helm Support**: Chart installation, upgrades, and management
- **🌐 Content Fetching**: Retrieve web page content on demand
- **🏢 LLM Farm Support**: Enterprise-ready with custom LLM endpoint support
- **📝 Comprehensive Logging**: Detailed request/response tracking

## 🏗️ Architecture

```
┌─────────────────┐    AG-UI Protocol    ┌─────────────────┐
│   Next.js       │◄──────────────────►│ Pydantic AI     │
│   Frontend      │                      │ Agent           │
│   (Port 3000)   │                      │ (Port 8000)     │
│                 │                      │                 │
│ ┌─────────────┐ │                      │ ┌─────────────┐ │
│ │ CopilotKit  │ │                      │ │ Tavily      │ │
│ │ Components  │ │                      │ │ Search      │ │
│ └─────────────┘ │                      │ └─────────────┘ │
└─────────────────┘                      │ ┌─────────────┐ │
                                         │ │ Kubernetes  │ │
                                         │ │ MCP Server  │ │
                                         │ └─────────────┘ │
                                         │ ┌─────────────┐ │
                                         │ │ Fetch MCP   │ │
                                         │ └─────────────┘ │
                                         └─────────────────┘
```

## 📋 Prerequisites

- **Python 3.12+** (for the agent)
- **Node.js 20+** (for the frontend)
- **kubectl** configured with cluster access
- **uvx** (for MCP server execution)
- **API Keys**:
  - OpenAI API key OR LLM Farm subscription key
  - Tavily API key

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install all dependencies (frontend + agent)
npm install
```

### 2. Configure Environment

Create `.env` file in the `agent/` directory:

```bash
cd agent
cp .env.example .env
```

Edit `.env` with your API keys:

```env
# For OpenAI (default)
USE_LLM_FARM=false
OPENAI_API_KEY=sk-your-key-here
TAVILY_API_KEY=tvly-your-key-here

# OR for LLM Farm
USE_LLM_FARM=true
LLM_FARM_API_KEY=your-farm-key-here
LLM_FARM_URL=https://your-farm-endpoint/
TAVILY_API_KEY=tvly-your-key-here
```

### 3. Configure Kubernetes Access

Ensure your kubeconfig is properly set:

```bash
# Check cluster access
kubectl cluster-info

# The agent will use your default kubeconfig at ~/.kube/config
# Or set KUBECONFIG environment variable
export KUBECONFIG=/path/to/your/kubeconfig
```

### 4. Run the Application

```bash
# Start both frontend and agent
npm run dev

# Or run separately:
npm run dev:ui      # Frontend only (http://localhost:3000)
npm run dev:agent   # Agent only (http://localhost:8000)
```

## 🛠️ Configuration

### MCP Servers

The agent supports multiple MCP servers configured in `agent/mcp_config.json`:

```json
{
  "mcpServers": {
    "kubernetes": {
      "command": "uvx",
      "args": ["mcp-server-kubernetes@latest"],
      "env": {
        "KUBECONFIG": "${KUBECONFIG:~/.kube/config}"
      }
    },
    "fetch": {
      "command": "uvx",
      "args": ["mcp-server-fetch"]
    }
  }
}
```

### LLM Farm Configuration

For enterprise deployments using LLM Farm:

1. Set `USE_LLM_FARM=true` in `.env`
2. Configure `LLM_FARM_API_KEY` with your subscription key
3. Update `LLM_FARM_URL` if using a custom endpoint

## 💡 Usage Examples

### Web Search
```
User: Search for latest Kubernetes 1.28 features
AI: [Uses Tavily to find and summarize latest K8s features]
```

### Kubernetes Operations
```
User: List all pods in the default namespace
AI: [Uses Kubernetes MCP to query pods]

User: Scale deployment nginx to 3 replicas
AI: [Uses Kubernetes MCP to scale deployment]
```

### Helm Operations
```
User: List all Helm releases
AI: [Uses Kubernetes MCP Helm tools]
```

### Content Fetching
```
User: Fetch content from https://kubernetes.io/docs/
AI: [Uses Fetch MCP to retrieve page content]
```

## 📁 Project Structure

```
chat-with-k8s/
├── agent/                      # Python Pydantic AI agent
│   ├── src/
│   │   ├── agent.py           # Main agent with MCP integration
│   │   └── main.py            # FastAPI entry point
│   ├── mcp_config.json        # MCP server configuration
│   ├── .env.example           # Environment template
│   ├── pyproject.toml         # Python dependencies
│   └── agent.log              # Runtime logs
├── src/                       # Next.js frontend
│   ├── app/
│   │   ├── api/copilotkit/
│   │   │   └── route.ts       # AG-UI integration
│   │   └── page.tsx           # Main chat interface
│   └── components/
│       └── ChatComponent.tsx  # Chat UI component
├── scripts/                   # Startup scripts
├── package.json              # Node.js dependencies
└── README.md                 # This file
```

## 🐛 Troubleshooting

### Agent Won't Start

1. Check Python version: `python --version` (need 3.12+)
2. Verify API keys in `.env`
3. Check logs: `cat agent/agent.log`

### Kubernetes Tools Not Working

1. Verify kubectl access: `kubectl cluster-info`
2. Check KUBECONFIG in `mcp_config.json`
3. Ensure `uvx` is installed: `pipx install uv`

### MCP Servers Not Loading

1. Check `agent.log` for MCP errors
2. Verify `uvx` is available: `which uvx`
3. Try minimal config: Use `mcp_config_minimal.json`

## 🔐 Security Considerations

- **API Keys**: Never commit `.env` files to version control
- **Kubeconfig**: Ensure proper RBAC permissions for cluster access
- **LLM Farm**: Use secure subscription keys and HTTPS endpoints

## 📚 Resources

- [Pydantic AI Documentation](https://ai.pydantic.dev/)
- [CopilotKit Documentation](https://docs.copilotkit.ai/)
- [MCP Server Kubernetes](https://github.com/Flux159/mcp-server-kubernetes)
- [Tavily API](https://tavily.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)

---

Built with ❤️ using Pydantic AI, CopilotKit, and Kubernetes
