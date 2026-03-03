.PHONY: install dev lint test seed clean

# Install all dependencies
install:
	cd frontend && pnpm install
	cd api && python -m uv sync
	cd ai && python -m uv sync

# Start all services for local development
dev:
	docker compose -f infra/docker-compose.yml up -d redis postgres
	@echo "Starting API server..."
	cd api && python -m uv run uvicorn app.main:app --reload --port 8000 &
	@echo "Starting ARQ worker..."
	cd api && python -m uv run arq app.workers.main.WorkerSettings &
	@echo "Starting frontend..."
	cd frontend && pnpm dev &
	@echo "All services started. API: http://localhost:8000 | Frontend: http://localhost:3000"

# Run linters
lint:
	cd frontend && pnpm lint
	cd api && python -m uv run ruff check .
	cd ai && python -m uv run ruff check .

# Run tests
test:
	cd frontend && pnpm test
	cd api && python -m uv run pytest
	cd ai && python -m uv run pytest

# Seed the database
seed:
	cd data && python -m uv run python scripts/seed_db.py

# Stop all services
clean:
	docker compose -f infra/docker-compose.yml down
	@echo "Stopped all Docker services"
