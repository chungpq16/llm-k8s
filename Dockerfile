# Next.js Development Dockerfile for Kubernetes
FROM node:20-alpine

# Install ca-certificates for custom CA support
RUN apk add --no-cache ca-certificates

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies (skip postinstall scripts)
RUN npm ci --ignore-scripts

# Copy source code
COPY . .

# Expose port
EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"
ENV NODE_ENV=development

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# Run development server with hot-reload
CMD ["npm", "run", "dev"]
