# Python Backend Dockerfile for Pydantic AI Agent
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for uv and MCP servers
RUN apt-get update && apt-get install -y \
    curl \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy custom CA certificate (optional)
# Uncomment and add your CA cert to the build context
# COPY custom-ca.crt /usr/local/share/ca-certificates/custom-ca.crt
# RUN update-ca-certificates

# Install uv package manager
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Copy Python project files
COPY pyproject.toml uv.lock* ./
COPY src/ ./src/
COPY mcp_config.json mcp_config_minimal.json ./

# Install Python dependencies using uv
RUN /root/.cargo/bin/uv sync --frozen

# Create directory for logs
RUN mkdir -p /app/logs

# Expose port for the agent API
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src:/app
ENV LOG_LEVEL=info
ENV HOST=0.0.0.0
ENV PORT=8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the agent using uv with full path
CMD ["/root/.cargo/bin/uv", "run", "python", "src/main.py"]
