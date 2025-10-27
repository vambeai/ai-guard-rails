.PHONY: help install run test docker-build docker-run docker-stop docker-dev docker-dev-stop clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install Python dependencies
	pip install -r requirements.txt

configure: ## Configure Guardrails Hub
	guardrails configure

install-validators: ## Install common validators
	@echo "Installing common validators..."
	guardrails hub install hub://guardrails/regex_match
	guardrails hub install hub://guardrails/competitor_check
	guardrails hub install hub://guardrails/toxic_language
	guardrails hub install hub://guardrails/detect_pii

run: ## Run the service locally
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

test: ## Run test script
	python test_api.py

# Docker commands
docker-build: ## Build Docker image
	docker build -t guardrails-validator:latest .

docker-run: ## Run Docker container
	docker run -d -p 8000:8000 --name guardrails-api guardrails-validator:latest

docker-stop: ## Stop and remove Docker container
	docker stop guardrails-api || true
	docker rm guardrails-api || true

docker-logs: ## View Docker container logs
	docker logs -f guardrails-api

# Docker Compose commands
compose-up: ## Start services with Docker Compose (production)
	docker-compose up -d

compose-down: ## Stop services with Docker Compose
	docker-compose down

compose-logs: ## View Docker Compose logs
	docker-compose logs -f

compose-restart: ## Restart Docker Compose services
	docker-compose restart

# Development with Docker Compose
docker-dev: ## Start development environment with hot reload
	docker-compose -f docker-compose.dev.yml up

docker-dev-stop: ## Stop development environment
	docker-compose -f docker-compose.dev.yml down

docker-dev-logs: ## View development logs
	docker-compose -f docker-compose.dev.yml logs -f

# Cleanup commands
clean: ## Clean up Python cache files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

clean-docker: ## Remove Docker images and containers
	docker-compose down -v || true
	docker-compose -f docker-compose.dev.yml down -v || true
	docker rmi guardrails-validator:latest || true
	docker rmi guardrails-validator:dev || true

# Setup commands
setup: install configure install-validators ## Complete setup (install, configure, validators)
	@echo "Setup complete! Run 'make run' to start the service."

# All-in-one commands
dev: ## Start local development server
	@echo "Starting development server..."
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

prod: compose-up ## Deploy with Docker Compose (production)
	@echo "Production deployment started!"
	@echo "API available at: http://localhost:8000"
	@echo "API docs at: http://localhost:8000/docs"

# Health check
health: ## Check if service is running
	@curl -s http://localhost:8000/health | python -m json.tool || echo "Service is not running"

