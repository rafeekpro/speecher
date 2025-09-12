# Speecher Project Makefile
# Docker-first testing strategy with enhanced developer experience

# Colors for better output
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color
BLUE := \033[0;34m

# Docker compose command
DOCKER_COMPOSE := docker-compose
TEST_COMPOSE := $(DOCKER_COMPOSE) --profile test

# Detect if running in CI environment
CI ?= false

.PHONY: help test test-local test-ci test-cleanup test-build dev dev-stop dev-logs dev-clean \
        db-shell db-backup db-restore docker-build docker-up docker-down docker-restart \
        install install-dev lint format clean info

# Default target
help: ## 📖 Show this help message
	@echo "$(BLUE)🚀 Speecher Project - Docker-First Development$(NC)"
	@echo "$(YELLOW)================================================$(NC)"
	@echo ""
	@echo "$(GREEN)Available Commands:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Quick Start:$(NC)"
	@echo "  make dev          # Start development environment"
	@echo "  make test         # Run tests in Docker"
	@echo "  make db-shell     # Connect to MongoDB"

# ============================================================================
# TESTING TARGETS - Docker-first strategy
# ============================================================================

test: test-local ## 🧪 Run tests (alias for test-local)

test-local: ## 🐳 Run tests in Docker containers (recommended)
	@echo "$(GREEN)🧪 Starting Docker-based test suite...$(NC)"
	@echo "$(YELLOW)📦 Building test container if needed...$(NC)"
	@$(TEST_COMPOSE) build test-runner 2>/dev/null || true
	@echo "$(YELLOW)🔄 Starting test dependencies...$(NC)"
	@$(DOCKER_COMPOSE) up -d mongodb
	@echo "$(YELLOW)⏳ Waiting for MongoDB to be healthy...$(NC)"
	@timeout 30 sh -c 'until docker compose ps mongodb | grep -q "healthy"; do sleep 1; done' || \
		(echo "$(RED)❌ MongoDB failed to start$(NC)" && exit 1)
	@echo "$(GREEN)🚀 Running tests in container...$(NC)"
	@$(TEST_COMPOSE) run --rm test-runner || \
		(echo "$(RED)❌ Tests failed! Check output above$(NC)" && exit 1)
	@echo "$(GREEN)✅ All tests passed!$(NC)"
	@echo "$(YELLOW)📊 Test results saved to ./test_results/$(NC)"

test-ci: ## 🤖 Run tests directly with pytest (for CI environment)
	@echo "$(GREEN)🤖 Running tests in CI mode...$(NC)"
	pytest tests/ -v --tb=short --junit-xml=test_results/results.xml

test-cleanup: ## 🧹 Clean up test containers and volumes
	@echo "$(YELLOW)🧹 Cleaning up test resources...$(NC)"
	@$(TEST_COMPOSE) down -v --remove-orphans
	@rm -rf test_results/
	@echo "$(GREEN)✅ Test cleanup complete$(NC)"

test-build: ## 🔨 Build test container
	@echo "$(YELLOW)🔨 Building test container...$(NC)"
	@$(TEST_COMPOSE) build test-runner
	@echo "$(GREEN)✅ Test container built successfully$(NC)"

test-watch: ## 👁️ Run tests in watch mode (auto-rerun on changes)
	@echo "$(GREEN)👁️ Starting test watch mode...$(NC)"
	@$(TEST_COMPOSE) run --rm test-runner pytest tests/ -v --watch

test-specific: ## 🎯 Run specific test file (usage: make test-specific FILE=test_api.py)
	@echo "$(GREEN)🎯 Running specific test: $(FILE)$(NC)"
	@$(TEST_COMPOSE) run --rm test-runner pytest tests/$(FILE) -v

# ============================================================================
# DEVELOPMENT TARGETS
# ============================================================================

dev: ## 🚀 Start development environment with Docker
	@echo "$(GREEN)🚀 Starting development environment...$(NC)"
	@echo "$(YELLOW)📦 Building containers if needed...$(NC)"
	@$(DOCKER_COMPOSE) build
	@echo "$(YELLOW)🔄 Starting services...$(NC)"
	@$(DOCKER_COMPOSE) up -d
	@echo "$(YELLOW)⏳ Waiting for services to be healthy...$(NC)"
	@sleep 5
	@$(DOCKER_COMPOSE) ps
	@echo ""
	@echo "$(GREEN)✅ Development environment ready!$(NC)"
	@echo ""
	@echo "$(BLUE)📍 Service URLs:$(NC)"
	@echo "  • Backend API:  http://localhost:8000"
	@echo "  • Frontend:     http://localhost:3000"
	@echo "  • MongoDB:      mongodb://localhost:27017"
	@echo ""
	@echo "$(YELLOW)💡 Useful commands:$(NC)"
	@echo "  • make dev-logs   - View container logs"
	@echo "  • make db-shell   - Connect to MongoDB"
	@echo "  • make dev-stop   - Stop all containers"

dev-stop: ## 🛑 Stop development containers
	@echo "$(YELLOW)🛑 Stopping development containers...$(NC)"
	@$(DOCKER_COMPOSE) stop
	@echo "$(GREEN)✅ Containers stopped$(NC)"

dev-logs: ## 📜 Show container logs
	@echo "$(BLUE)📜 Showing container logs (Ctrl+C to exit)...$(NC)"
	@$(DOCKER_COMPOSE) logs -f

dev-logs-backend: ## 📜 Show backend logs only
	@$(DOCKER_COMPOSE) logs -f backend

dev-logs-frontend: ## 📜 Show frontend logs only
	@$(DOCKER_COMPOSE) logs -f frontend

dev-clean: ## 🗑️ Complete cleanup including volumes
	@echo "$(RED)⚠️  Warning: This will delete all data!$(NC)"
	@echo "Press Ctrl+C to cancel, or wait 5 seconds to continue..."
	@sleep 5
	@echo "$(YELLOW)🗑️  Performing complete cleanup...$(NC)"
	@$(DOCKER_COMPOSE) down -v --remove-orphans
	@docker system prune -f
	@echo "$(GREEN)✅ Complete cleanup done$(NC)"

dev-restart: ## 🔄 Restart development environment
	@echo "$(YELLOW)🔄 Restarting development environment...$(NC)"
	@$(MAKE) dev-stop
	@$(MAKE) dev

dev-rebuild: ## 🔨 Rebuild and restart containers
	@echo "$(YELLOW)🔨 Rebuilding containers...$(NC)"
	@$(DOCKER_COMPOSE) build --no-cache
	@$(MAKE) dev-restart

# ============================================================================
# DATABASE TARGETS
# ============================================================================

db-shell: ## 🗄️ Connect to MongoDB shell
	@echo "$(BLUE)🗄️ Connecting to MongoDB shell...$(NC)"
	@docker exec -it speecher-mongodb mongosh -u admin -p speecher_admin_pass

db-backup: ## 💾 Backup database
	@echo "$(YELLOW)💾 Creating database backup...$(NC)"
	@mkdir -p backups
	@docker exec speecher-mongodb mongodump \
		--username=admin \
		--password=speecher_admin_pass \
		--authenticationDatabase=admin \
		--archive=/tmp/backup_$$(date +%Y%m%d_%H%M%S).gz \
		--gzip
	@docker cp speecher-mongodb:/tmp/backup_$$(date +%Y%m%d_%H%M%S).gz ./backups/
	@echo "$(GREEN)✅ Backup saved to ./backups/$(NC)"

db-restore: ## 📥 Restore database from backup (usage: make db-restore BACKUP=backup_file.gz)
	@if [ -z "$(BACKUP)" ]; then \
		echo "$(RED)❌ Please specify BACKUP file$(NC)"; \
		echo "Usage: make db-restore BACKUP=backup_file.gz"; \
		exit 1; \
	fi
	@echo "$(YELLOW)📥 Restoring database from $(BACKUP)...$(NC)"
	@docker cp ./backups/$(BACKUP) speecher-mongodb:/tmp/restore.gz
	@docker exec speecher-mongodb mongorestore \
		--username=admin \
		--password=speecher_admin_pass \
		--authenticationDatabase=admin \
		--archive=/tmp/restore.gz \
		--gzip \
		--drop
	@echo "$(GREEN)✅ Database restored$(NC)"

db-reset: ## 🔄 Reset database to initial state
	@echo "$(RED)⚠️  This will delete all data!$(NC)"
	@echo "Press Ctrl+C to cancel, or wait 3 seconds..."
	@sleep 3
	@docker exec speecher-mongodb mongosh \
		-u admin -p speecher_admin_pass \
		--eval "use speecher; db.dropDatabase();"
	@echo "$(GREEN)✅ Database reset complete$(NC)"

# ============================================================================
# DOCKER MANAGEMENT
# ============================================================================

docker-build: ## 🔨 Build all Docker images
	@echo "$(YELLOW)🔨 Building all Docker images...$(NC)"
	@$(DOCKER_COMPOSE) build
	@echo "$(GREEN)✅ All images built$(NC)"

docker-up: ## ⬆️ Start all services
	@$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)✅ All services started$(NC)"

docker-down: ## ⬇️ Stop all services
	@$(DOCKER_COMPOSE) down
	@echo "$(GREEN)✅ All services stopped$(NC)"

docker-restart: ## 🔄 Restart all services
	@$(MAKE) docker-down
	@$(MAKE) docker-up

docker-ps: ## 📊 Show container status
	@$(DOCKER_COMPOSE) ps

docker-logs: ## 📜 Show all container logs
	@$(DOCKER_COMPOSE) logs -f

# ============================================================================
# LOCAL DEVELOPMENT (without Docker)
# ============================================================================

install: ## 📦 Install production dependencies
	pip install -r requirements/base.txt

install-dev: ## 📦 Install all dependencies (including dev and test)
	pip install -r requirements/base.txt
	pip install -r requirements/dev.txt
	pip install -r requirements/test.txt

run-backend-local: ## 🏃 Run FastAPI backend locally
	cd src/backend && uvicorn main:app --reload --port 8000

run-frontend-local: ## 🏃 Run React frontend locally
	cd src/react-frontend && npm start

# ============================================================================
# CODE QUALITY
# ============================================================================

lint: ## 🔍 Run all linters
	@echo "$(YELLOW)🔍 Running linters...$(NC)"
	flake8 src/ tests/ --max-line-length=120 --ignore=E203,W503
	pylint src/ --exit-zero
	mypy src/ --ignore-missing-imports

format: ## 🎨 Format code with black and isort
	@echo "$(YELLOW)🎨 Formatting code...$(NC)"
	black src/ tests/ scripts/
	isort src/ tests/ scripts/
	@echo "$(GREEN)✅ Code formatted$(NC)"

check-format: ## ✅ Check if code is formatted correctly
	black --check src/ tests/ scripts/
	isort --check-only src/ tests/ scripts/

# ============================================================================
# CLEANUP
# ============================================================================

clean: ## 🧹 Remove generated files and caches
	@echo "$(YELLOW)🧹 Cleaning up generated files...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name ".coverage" -delete
	@rm -rf htmlcov/
	@rm -rf .pytest_cache/
	@rm -rf .mypy_cache/
	@rm -rf dist/
	@rm -rf build/
	@rm -rf *.egg-info
	@echo "$(GREEN)✅ Cleanup complete$(NC)"

clean-docker: ## 🗑️ Remove Docker volumes and orphan containers
	@echo "$(YELLOW)🗑️ Cleaning Docker resources...$(NC)"
	@$(DOCKER_COMPOSE) down -v --remove-orphans
	@echo "$(GREEN)✅ Docker cleanup complete$(NC)"

clean-all: clean clean-docker ## 🧹 Complete cleanup
	@echo "$(GREEN)✅ Complete cleanup done$(NC)"

# ============================================================================
# PROJECT INFO
# ============================================================================

info: ## ℹ️ Show project information
	@echo "$(BLUE)ℹ️  Project Information$(NC)"
	@echo "========================"
	@echo "Project: Speecher"
	@echo "Python: $$(python --version 2>&1)"
	@echo "Docker: $$(docker --version 2>&1)"
	@echo "Docker Compose: $$(docker compose --version 2>&1)"
	@echo "Current Branch: $$(git branch --show-current)"
	@echo "Last Commit: $$(git log -1 --oneline)"
	@echo ""
	@echo "$(YELLOW)Container Status:$(NC)"
	@$(DOCKER_COMPOSE) ps 2>/dev/null || echo "No containers running"

status: ## 📊 Show full system status
	@$(MAKE) info
	@echo ""
	@echo "$(YELLOW)Disk Usage:$(NC)"
	@docker system df
	@echo ""
	@echo "$(YELLOW)Network Status:$(NC)"
	@docker network ls | grep speecher || echo "No speecher network found"

# ============================================================================
# SHORTCUTS
# ============================================================================

d: dev ## Shortcut for 'make dev'
t: test ## Shortcut for 'make test'
l: dev-logs ## Shortcut for 'make dev-logs'
s: dev-stop ## Shortcut for 'make dev-stop'