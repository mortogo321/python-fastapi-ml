.PHONY: help install dev prod down clean logs test format lint venv

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Virtual environment commands
venv: ## Create and setup virtual environment
	./scripts/setup-venv.sh

venv-activate: ## Show command to activate venv
	@echo "Run: source venv/bin/activate"

install: ## Install dependencies in active venv
	pip install --upgrade pip
	pip install -r requirements.txt

install-dev: ## Install dev dependencies in active venv
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

# Docker commands
dev: ## Start development environment with Docker
	cd docker && docker-compose --profile development up --build

prod: ## Start production environment with Docker
	cd docker && docker-compose --profile production up --build -d

down: ## Stop all Docker containers
	cd docker && docker-compose --profile development --profile production down

clean: ## Stop containers and remove volumes
	cd docker && docker-compose --profile development --profile production down -v
	docker system prune -f

logs: ## Show logs from all containers
	cd docker && docker-compose logs -f

logs-api: ## Show API logs
	cd docker && docker-compose logs -f api-dev api-prod

logs-db: ## Show database logs
	cd docker && docker-compose logs -f postgres

logs-ollama: ## Show Ollama logs
	cd docker && docker-compose logs -f ollama

# Docker service management
setup-ollama: ## Pull Ollama model (Docker)
	cd docker && docker-compose exec ollama ollama pull llama2

init-db: ## Initialize database (Docker)
	cd docker && docker-compose exec api-dev python -m app.db.init_db

shell-api: ## Open shell in API container
	cd docker && docker-compose exec api-dev /bin/bash

shell-db: ## Open PostgreSQL shell
	cd docker && docker-compose exec postgres psql -U postgres -d fastapi_ml_db

restart: ## Restart all services
	cd docker && docker-compose --profile development --profile production restart

ps: ## Show running containers
	cd docker && docker-compose ps

seed: ## Seed database with sample data (Docker)
	cd docker && docker-compose exec api-dev python scripts/seed_data.py

# Local development commands (venv)
run-local: ## Run app locally (requires venv)
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

init-db-local: ## Initialize local database
	python -m app.db.init_db

seed-local: ## Seed local database
	python scripts/seed_data.py

# Testing and quality
test: ## Run tests
	pytest tests/ -v

test-cov: ## Run tests with coverage
	pytest tests/ --cov=app --cov-report=html --cov-report=term

format: ## Format code with black
	black app/ tests/

format-check: ## Check code formatting
	black app/ tests/ --check

lint: ## Lint code with flake8
	flake8 app/ tests/ --max-line-length=100

quality: ## Run all quality checks
	black app/ tests/ --check
	flake8 app/ tests/ --max-line-length=100
	mypy app/

# Cleanup
clean-pyc: ## Remove Python file artifacts
	find . -type f -name '*.py[co]' -delete
	find . -type d -name '__pycache__' -delete

clean-venv: ## Remove virtual environment
	rm -rf venv venv*/

clean-all: ## Clean everything
	make clean-pyc
	make clean-venv
	make clean
