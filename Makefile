.PHONY: help build up down logs clean restart agent frontend dev

# Default target
help:
	@echo "Chat with K8s - Docker Commands"
	@echo "================================"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  help        Show this help message"
	@echo "  build       Build all Docker images"
	@echo "  up          Start all services"
	@echo "  down        Stop all services"
	@echo "  logs        View logs from all services"
	@echo "  clean       Remove containers, volumes, and images"
	@echo "  restart     Restart all services"
	@echo "  agent       View agent logs only"
	@echo "  frontend    View frontend logs only"
	@echo "  dev         Run in development mode (hot-reload)"
	@echo ""

# Build all Docker images
build:
	@echo "Building Docker images..."
	docker-compose build

# Start all services
up:
	@echo "Starting services..."
	docker-compose up -d
	@echo ""
	@echo "Services started!"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend:  http://localhost:8000"

# Stop all services
down:
	@echo "Stopping services..."
	docker-compose down

# View logs from all services
logs:
	docker-compose logs -f

# Clean up everything
clean:
	@echo "Cleaning up Docker resources..."
	docker-compose down -v --rmi all
	@echo "Cleanup complete!"

# Restart all services
restart: down up

# View agent logs only
agent:
	docker-compose logs -f agent

# View frontend logs only
frontend:
	docker-compose logs -f frontend

# Run in development mode
dev:
	@echo "Starting development mode with hot-reload..."
	npm run dev

# Build and run
start: build up
	@echo ""
	@echo "Services are starting..."
	@echo "Use 'make logs' to view logs"
	@echo "Use 'make down' to stop services"
