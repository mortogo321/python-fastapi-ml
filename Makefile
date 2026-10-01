.PHONY: lint test typecheck check build up down

lint:
	ruff check .
	ruff format --check .

test:
	pytest -q

typecheck:
	mypy app

check: lint typecheck test

build:
	docker build -t python-fastapi-ml .

up:
	docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml --profile development up --build

prod:
	docker compose -f docker/docker-compose.yml -f docker/docker-compose.prod.yml --profile production up --build -d

down:
	docker compose -f docker/docker-compose.yml --profile development --profile production down

setup-ollama:
	docker compose -f docker/docker-compose.yml exec ollama ollama pull llama3.2

init-db:
	docker compose -f docker/docker-compose.yml --profile development exec api-dev python -m app.db.init_db
