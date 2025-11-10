
"""
Main entry point for the Kubernetes AI Chatbot agent.

This module starts the Uvicorn server with the AG-UI compatible agent.
"""

import uvicorn
from agent import app, logger

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("🚀 Starting Kubernetes AI Chatbot")
    logger.info("=" * 60)
    logger.info("📝 Logging enabled - check agent.log for detailed logs")
    logger.info("🤖 Agent with Tavily search + Kubernetes MCP tools")
    logger.info("🌐 Server starting on http://0.0.0.0:8000")
    logger.info("🔗 AG-UI endpoint: http://0.0.0.0:8000/")
    logger.info("ℹ️  Tools endpoint: http://0.0.0.0:8000/tools")
    logger.info("⚙️  Configure .env with your API keys")
    logger.info("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True
    )

