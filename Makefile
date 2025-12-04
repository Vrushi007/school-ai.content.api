.PHONY: help build build-prod up up-local up-prod down restart logs migrate upgrade shell test clean setup-local seed seed-docker

help:
	@echo "Available commands:"
	@echo "  make build       - Build Docker images (development)"
	@echo "  make build-prod   - Build production Docker images"
	@echo "  make up          - Start services (with Docker PostgreSQL)"
	@echo "  make up-local    - Start service (with local PostgreSQL)"
	@echo "  make up-prod     - Start production service"
	@echo "  make down        - Stop services"
	@echo "  make restart    - Restart services"
	@echo "  make logs        - View logs"
	@echo "  make migrate     - Create new migration"
	@echo "  make upgrade     - Run migrations"
	@echo "  make seed        - Seed database with initial data (local)"
	@echo "  make seed-docker - Seed database with initial data (Docker)"
	@echo "  make shell       - Open shell in container"
	@echo "  make test        - Run tests"
	@echo "  make clean       - Clean up containers and volumes"
	@echo "  make setup-local - Setup for local development"

build:
	docker compose build

build-prod:
	docker compose -f docker-compose.prod.yml build

up:
	docker compose up -d

up-local:
	docker compose -f docker-compose.local.yml up -d

up-prod:
	docker compose -f docker-compose.prod.yml up -d

down:
	docker compose down

restart:
	docker compose restart

logs:
	docker compose logs -f

migrate:
	docker compose exec content-service alembic revision --autogenerate -m "$(msg)"

upgrade:
	docker compose exec content-service alembic upgrade head

seed:
	python seed_data.py

seed-docker:
	docker compose exec content-service python seed_data.py

shell:
	docker compose exec content-service /bin/bash

test:
	docker compose exec content-service pytest

clean:
	docker compose down -v
	docker system prune -f

setup-local:
	@echo "Setting up for local development..."
	@echo "1. Creating virtual environment..."
	python3.11 -m venv venv || true
	@echo "2. Installing dependencies..."
	./venv/bin/pip install -r requirements.txt || pip install -r requirements.txt
	@echo ""
	@echo "✅ Setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Activate virtual environment: source venv/bin/activate"
	@echo "  2. Create .env file with your DATABASE_URL"
	@echo "  3. Run: alembic upgrade head"
	@echo "  4. Run: uvicorn app.main:app --reload"

