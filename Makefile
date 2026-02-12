.PHONY: dev dev-build down logs test lint migrate seed clean

# ---- Docker Compose ----
dev:
	docker compose -f infra/docker/docker-compose.yml -f infra/docker/docker-compose.dev.yml up

dev-build:
	docker compose -f infra/docker/docker-compose.yml -f infra/docker/docker-compose.dev.yml up --build

down:
	docker compose -f infra/docker/docker-compose.yml -f infra/docker/docker-compose.dev.yml down -v

logs:
	docker compose -f infra/docker/docker-compose.yml -f infra/docker/docker-compose.dev.yml logs -f

# ---- Backend ----
test-backend:
	cd backend && python -m pytest tests/ -v

lint-backend:
	cd backend && ruff check app/ && ruff format --check app/

# ---- Frontend ----
test-frontend:
	cd frontend && npm run test

lint-frontend:
	cd frontend && npm run lint

# ---- Combined ----
test: test-backend test-frontend
lint: lint-backend lint-frontend

# ---- Database ----
migrate:
	cd backend && alembic upgrade head

seed:
	cd backend && python -m app.seed

# ---- Cleanup ----
clean:
	docker compose -f infra/docker/docker-compose.yml down -v --rmi local
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name node_modules -exec rm -rf {} + 2>/dev/null || true
