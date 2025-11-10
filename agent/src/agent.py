"""
GenAI Chatbot with Pydantic AI, Tavily Search, and MCP Integration

This agent uses Pydantic AI framework with:
- Tavily search tool for web search capabilities
- Multiple MCP servers for extended functionality
- AG-UI protocol for CopilotKit integration
- Configurable MCP servers via JSON config
"""

import os
import asyncio
import logging
import json
import subprocess
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.mcp import load_mcp_servers
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from openai import AsyncOpenAI
from tavily import TavilyClient
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Check if required API keys are available
# For LLM Farm, we need LLM_FARM_API_KEY instead of OPENAI_API_KEY
use_llm_farm = os.getenv("USE_LLM_FARM", "false").lower() == "true"

if use_llm_farm:
    required_keys = ["LLM_FARM_API_KEY", "TAVILY_API_KEY"]
    llm_farm_url = os.getenv("LLM_FARM_URL", "https://aoai-farm.bosch-temp.com/api/openai/deployments/askbosch-prod-farm-openai-gpt-4o-mini-2024-07-18/")
    logger.info("Using LLM Farm custom endpoint")
else:
    required_keys = ["OPENAI_API_KEY", "TAVILY_API_KEY"]
    logger.info("Using standard OpenAI API")

missing_keys = [key for key in required_keys if not os.getenv(key)]

if missing_keys:
    logger.error(f"Missing required environment variables: {', '.join(missing_keys)}")
    raise ValueError(f"Missing required environment variables: {', '.join(missing_keys)}")

logger.info("Environment variables loaded successfully")

# Initialize Tavily client
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
logger.info("Tavily client initialized")

# Load MCP servers from configuration
def load_mcp_config(config_path: str = "mcp_config.json"):
    """Load MCP server configuration from JSON file with robust error handling"""
    try:
        if os.path.exists(config_path):
            logger.info(f"Loading MCP configuration from {config_path}")
            
            # First, validate the JSON structure
            with open(config_path, 'r') as f:
                config_data = json.load(f)
                logger.info(f"Found {len(config_data.get('mcpServers', {}))} MCP server definitions")
            
            # Try to load the MCP servers
            mcp_servers = load_mcp_servers(config_path)
            logger.info(f"✅ Successfully loaded {len(mcp_servers)} MCP servers")
            return mcp_servers
        else:
            logger.warning(f"MCP config file {config_path} not found")
            # Try the minimal config as fallback
            if config_path != "mcp_config_minimal.json" and os.path.exists("mcp_config_minimal.json"):
                logger.info("Trying minimal config as fallback...")
                return load_mcp_config("mcp_config_minimal.json")
            logger.warning("No MCP config found, proceeding with Tavily search only")
            return []
    except FileNotFoundError as e:
        logger.error(f"❌ MCP config file not found: {e}")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"❌ Invalid JSON in MCP config: {e}")
        return []
    except ImportError as e:
        logger.error(f"❌ MCP dependencies not installed: {e}")
        logger.info("Install with: pip install 'pydantic-ai[mcp]'")
        return []
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ MCP server subprocess failed: {e}")
        logger.info("Check that required tools (uvx, npx, deno) are installed")
        return []
    except Exception as e:
        logger.error(f"❌ Failed to load MCP configuration: {type(e).__name__}: {e}")
        logger.info("Continuing with Tavily search only...")
        return []

# Load MCP servers
mcp_servers = load_mcp_config()

# Log loaded MCP servers
if mcp_servers:
    logger.info("🔧 Available MCP toolsets:")
    for i, server in enumerate(mcp_servers, 1):
        server_name = getattr(server, '_name', server.__class__.__name__)
        logger.info(f"  {i}. {server_name}")
else:
    logger.info("📝 No MCP servers loaded - only Tavily search will be available")


# Initialize the model (LLM Farm or OpenAI)
def initialize_model():
    """Initialize the AI model based on configuration"""
    if use_llm_farm:
        logger.info("🔧 Configuring LLM Farm client...")
        
        # Configure AsyncOpenAI client for LLM Farm
        llm_client = AsyncOpenAI(
            base_url=llm_farm_url,
            api_key="dummy",  # LLM Farm doesn't use standard API key
            default_headers={"genaiplatform-farm-subscription-key": os.getenv("LLM_FARM_API_KEY")},
            default_query={"api-version": "2024-08-01-preview"}
        )
        
        # Create Pydantic AI model with custom client
        model = OpenAIChatModel(
            model_name="gpt-4o-mini",
            provider=OpenAIProvider(openai_client=llm_client)
        )
        
        logger.info(f"✓ LLM Farm client configured: {llm_farm_url}")
        return model
    else:
        logger.info("✓ Using standard OpenAI API: gpt-4o-mini")
        return "openai:gpt-4o-mini"

model = initialize_model()


class SearchResult(BaseModel):
    """Search result from Tavily"""
    title: str = Field(description="Title of the search result")
    url: str = Field(description="URL of the search result")
    content: str = Field(description="Content snippet from the search result")
    score: float = Field(description="Relevance score of the result")


class SearchResponse(BaseModel):
    """Response from search operation"""
    query: str = Field(description="The search query that was executed")
    results: List[SearchResult] = Field(description="List of search results")
    answer: Optional[str] = Field(description="AI-generated answer based on search results")


# Initialize the Pydantic AI agent with MCP servers
agent = Agent(
    model,
    system_prompt="""
    You are a helpful AI assistant with access to multiple tools. Choose the appropriate tool based on the user's request:
    
    **Tool Selection Guidelines:**
    
    1. **Web Search (tavily_search)** - Use when the user wants to SEARCH for information:
       - Keywords: "search", "find", "look up", "what's happening", "latest news", "research"
       - Examples: "Search for latest AI developments", "Find information about...", "What's new in..."
       - Use for: Current events, news, research topics, general information discovery
    
    2. **Kubernetes & Helm Operations (MCP)** - Use when the user wants to interact with Kubernetes or Helm:
       
       **Kubernetes Operations:**
       - Keywords: "kubectl", "kubernetes", "k8s", "pods", "services", "deployments", "namespaces", "CRDs", "custom resources"
       - Resource Management: Query supported resource types (built-in and custom resources)
       - Read Operations: get resource details, list resources with filtering, describe resources
       - Write Operations: create, update, delete resources (fine-grained control available)
       - Examples: "Get pods in namespace", "List deployments", "Describe service", "Create configmap", "Delete pod"
       - Supports: All Kubernetes resource types including custom resources, namespace filtering
       
       **Helm Operations:**
       - Keywords: "helm", "charts", "releases", "repositories", "install", "upgrade", "uninstall"
       - Release Management: list, get, install, upgrade, uninstall Helm releases
       - Repository Management: list, add, remove Helm repositories
       - Examples: "List helm releases", "Install chart", "Upgrade release", "Add helm repo"
       - Fine-grained control: Each operation can be independently enabled/disabled
       
       **Connection:** Uses kubeconfig for cluster authentication
    
    3. **Fetch Tool (MCP)** - Use when the user wants to FETCH content from a specific URL:
       - Keywords: "fetch", "get content from", "retrieve from URL", "download", "scrape"
       - Examples: "Fetch content from https://...", "Get the content of this webpage", "Retrieve data from..."
       - Use for: Getting specific webpage content, downloading data from URLs
    
    4. **Direct LLM Response** - Use when the request doesn't involve search, fetch, Kubernetes, or Helm:
       - General questions, explanations, analysis of provided text
       - Math problems, coding help, creative writing, advice
       - Processing or analyzing content the user has already provided
       - Examples: "Explain how...", "Write a story about...", "Calculate...", "Help me understand..."
    
    **Additional MCP Tools** (if available):
    - Python code execution for calculations and data processing
    - Memory storage for remembering information across conversations
    - File operations for saving/loading data
    - GitHub operations for repository management
    
    **Instructions:**
    - Always choose the most appropriate tool based on the user's intent
    - For search requests: Use tavily_search and provide comprehensive results with citations
    - For Kubernetes/Helm requests: Use the appropriate MCP tools for cluster and Helm operations
    - For fetch requests: Use the MCP fetch tool to retrieve specific URL content
    - For general questions: Respond directly using your knowledge without tools
    - Be conversational, helpful, and thorough in your responses
    - If uncertain about tool choice, ask the user to clarify their intent
    - When using Kubernetes tools, specify namespace when needed (default to 'default' if not specified)
    - For Helm operations, consider asking for release names, chart names, or repository details as needed
    """,
    toolsets=mcp_servers,  # Add MCP servers as toolsets
)

logger.info(f"🤖 Pydantic AI agent initialized with GPT-4o-mini")
logger.info(f"🔧 Total toolsets available: {len(mcp_servers) + 1} (Tavily + {len(mcp_servers)} MCP servers)")


@agent.tool_plain
async def tavily_search(query: str) -> SearchResponse:
    """
    Search the web using Tavily for current information and real-time data.
    
    Args:
        query: The search query to execute
        
    Returns:
        SearchResponse with results and AI-generated answer
    """
    request_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    logger.info(f"[{request_id}] 🔍 TOOL CALLED: tavily_search")
    logger.info(f"[{request_id}] Query: '{query}'")
    
    try:
        # Run the synchronous tavily search in a thread pool
        logger.info(f"[{request_id}] Executing Tavily search...")
        loop = asyncio.get_event_loop()
        search_result = await loop.run_in_executor(
            None,
            lambda: tavily_client.search(
                query=query,
                search_depth="advanced",
                include_answer=True,
                max_results=5,
                include_raw_content=True
            )
        )
        
        logger.info(f"[{request_id}] Tavily search completed successfully")
        logger.info(f"[{request_id}] Found {len(search_result.get('results', []))} results")
        
        # Process the results
        results = []
        for i, result in enumerate(search_result.get("results", [])):
            search_res = SearchResult(
                title=result.get("title", ""),
                url=result.get("url", ""),
                content=result.get("content", ""),
                score=result.get("score", 0.0)
            )
            results.append(search_res)
            logger.debug(f"[{request_id}] Result {i+1}: {result.get('title', 'No title')} - {result.get('url', 'No URL')}")
        
        response = SearchResponse(
            query=query,
            results=results,
            answer=search_result.get("answer", "")
        )
        
        logger.info(f"[{request_id}] ✅ TOOL SUCCESS: tavily_search returned {len(results)} results")
        if search_result.get("answer"):
            logger.info(f"[{request_id}] AI Answer available: {search_result.get('answer')[:100]}...")
        
        return response
        
    except Exception as e:
        logger.error(f"[{request_id}] ❌ TOOL ERROR: tavily_search failed with error: {str(e)}")
        logger.error(f"[{request_id}] Error details: {type(e).__name__}: {e}")
        
        # Return error information in a structured way
        error_response = SearchResponse(
            query=query,
            results=[],
            answer=f"Search failed: {str(e)}"
        )
        
        logger.info(f"[{request_id}] Returning error response to user")
        return error_response


# Expose the agent as an AG-UI compatible ASGI application
app = agent.to_ag_ui()

# Add middleware to log requests
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import time

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        request_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        
        # Log incoming request
        logger.info(f"[{request_id}] 📨 INCOMING REQUEST: {request.method} {request.url.path}")
        logger.info(f"[{request_id}] Headers: {dict(request.headers)}")
        
        # Get request body for POST requests
        if request.method == "POST":
            body = await request.body()
            if body:
                try:
                    # Try to parse as JSON for better logging
                    body_json = json.loads(body.decode())
                    logger.info(f"[{request_id}] Request body: {json.dumps(body_json, indent=2)}")
                except:
                    logger.info(f"[{request_id}] Request body (raw): {body.decode()[:500]}...")
        
        # Process the request
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        logger.info(f"[{request_id}] 📤 RESPONSE: {response.status_code} (took {process_time:.2f}s)")
        
        return response

# Add the middleware to the app
app.add_middleware(RequestLoggingMiddleware)

logger.info("AG-UI compatible ASGI application created with request logging middleware")

if __name__ == "__main__":
    import uvicorn
    
    logger.info("=" * 60)
    logger.info("🚀 Starting Enhanced Pydantic AI Agent")
    logger.info("=" * 60)
    logger.info("📝 Logging enabled - check agent.log for detailed logs")
    logger.info(f"🤖 Model: {'LLM Farm (Custom)' if use_llm_farm else 'OpenAI GPT-4o-mini'}")
    logger.info("🔧 Built-in tools: tavily_search")
    if mcp_servers:
        logger.info("🔧 MCP servers loaded - additional tools available")
        logger.info("   Check /tools endpoint to see all available tools")
    else:
        logger.info("📝 No MCP servers - only built-in tools available")
    logger.info("🌐 Server starting on http://0.0.0.0:8000")
    logger.info("🔗 AG-UI endpoint: http://0.0.0.0:8000/")
    logger.info("ℹ️  Tools endpoint: http://0.0.0.0:8000/tools")
    if use_llm_farm:
        logger.info("⚙️  Environment: Set LLM_FARM_API_KEY and TAVILY_API_KEY")
    else:
        logger.info("⚙️  Environment: Set OPENAI_API_KEY and TAVILY_API_KEY")
    logger.info("=" * 60)
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info",
        access_log=True
    )