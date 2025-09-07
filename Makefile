# Speecher Project Makefile
# Professional build automation

.PHONY: help install install-dev test test-coverage lint format clean docker-build docker-up docker-down docker-restart run-backend run-frontend

# Default target
help: ## Show this help message
	@echo "Speecher Project - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Installation
install: ## Install production dependencies
	pip install -r requirements/base.txt

install-dev: ## Install all dependencies (including dev and test)
	pip install -r requirements/base.txt
	pip install -r requirements/dev.txt
	pip install -r requirements/test.txt

install-azure: ## Install Azure-specific dependencies
	pip install -r requirements/azure.txt

# Testing
test: ## Run all tests
	pytest tests/ -v

test-coverage: ## Run tests with coverage report
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term

test-api: ## Run API tests only
	./scripts/test/run_api_tests.sh

test-integration: ## Run integration tests
	pytest tests/test_integration.py -v

# Code Quality
lint: ## Run all linters
	flake8 src/ tests/ --max-line-length=120 --ignore=E203,W503
	pylint src/ --exit-zero
	mypy src/ --ignore-missing-imports

format: ## Format code with black and isort
	black src/ tests/ scripts/
	isort src/ tests/ scripts/

check-format: ## Check if code is formatted correctly
	black --check src/ tests/ scripts/
	isort --check-only src/ tests/ scripts/

# Docker
docker-build: ## Build all Docker images
	docker-compose build

docker-up: ## Start all services
	./scripts/docker/start.sh

docker-down: ## Stop all services
	./scripts/docker/stop.sh

docker-restart: docker-down docker-up ## Restart all services

docker-logs: ## Show Docker logs
	docker-compose logs -f

docker-test: ## Run tests in Docker
	./scripts/docker/test.sh

# Development
run-backend: ## Run FastAPI backend locally
	cd src/backend && uvicorn main:app --reload --port 8000

run-frontend: ## Run React frontend locally
	cd src/react-frontend && npm start

run-streamlit: ## Run Streamlit frontend (legacy)
	cd src/frontend && streamlit run app.py

dev: ## Run development environment
	python scripts/dev/devmanager.py start

debug: ## Run backend in debug mode
	python scripts/dev/debug_backend.py

generate-audio: ## Generate test audio files
	python scripts/dev/generate_test_audio.py

# Database
db-shell: ## Connect to MongoDB shell
	docker exec -it speecher-mongodb mongosh

db-backup: ## Backup MongoDB database
	docker exec speecher-mongodb sh -c 'mkdir -p /backup && mongodump --out /backup/$(date +%Y%m%d_%H%M%S)'

# Cleanup
clean: ## Remove generated files and caches
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info

clean-docker: ## Remove Docker volumes and orphan containers
	docker-compose down -v --remove-orphans

# Git
commit: ## Quick commit with message (usage: make commit m="your message")
	git add . && git commit -m "$(m)"

push: ## Push to current branch
	git push origin $(shell git branch --show-current)

pull: ## Pull and rebase from current branch
	git pull --rebase origin $(shell git branch --show-current)

# Project Info
info: ## Show project information
	@echo "Project: Speecher"
	@echo "Python: $(shell python --version)"
	@echo "Current Branch: $(shell git branch --show-current)"
	@echo "Last Commit: $(shell git log -1 --oneline)"

# Requirements
freeze: ## Freeze current pip packages
	pip freeze > requirements/current.txt

update-deps: ## Update all dependencies
	pip install --upgrade -r requirements/base.txt
	pip install --upgrade -r requirements/dev.txt
	pip install --upgrade -r requirements/test.txt