# Combined Dockerfile for Frontend + Backend
# Start with Python base (has uv support) and add Node.js
FROM python:3.12-slim

# Install Node.js 20.x, npm, and other dependencies
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    git \
    bash \
    gnupg \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list \
    && apt-get update \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install uv for Python package management
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    /root/.local/bin/uv --version
ENV PATH="/root/.local/bin:$PATH"

# Copy and install frontend dependencies
COPY package.json package-lock.json* ./
RUN npm ci --ignore-scripts

# Copy frontend source code
COPY src ./src
COPY public ./public
COPY next.config.ts tsconfig.json postcss.config.mjs ./

# Copy and install Python agent
COPY agent/pyproject.toml agent/uv.lock* ./agent/
COPY agent/src ./agent/src/
COPY agent/mcp_config*.json ./agent/

WORKDIR /app/agent
RUN uv sync --frozen

# Create logs directory
RUN mkdir -p /app/agent/logs

WORKDIR /app

# Expose both ports
EXPOSE 3000 8000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"
ENV NODE_ENV=development
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/agent/src:/app/agent

# Health check for both services
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:3000/ && curl -f http://localhost:8000/ || exit 1

# Start both services directly (not via npm scripts)
CMD ["bash", "-c", "cd /app/agent && uv run python src/main.py & cd /app && npx next dev --turbopack --hostname 0.0.0.0"]
