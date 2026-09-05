.PHONY: install run dev test coverage lint format clean docker-up docker-down

install:
	pip install -e .

run:
	cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

dev:
	cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

test:
	pytest -v

coverage:
	pytest --cov=app --cov-report=term-missing --cov-report=html

lint:
	ruff check .

format:
	black .
	ruff check . --fix

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

db-migrate:
	cd backend && alembic upgrade head

db-revision:
	cd backend && alembic revision --autogenerate -m "$(message)"

help:
	@echo "Available commands:"
	@echo "  make install       Install project dependencies"
	@echo "  make run           Run production server"
	@echo "  make dev           Run development server (with auto-reload)"
	@echo "  make test          Run tests"
	@echo "  make coverage      Run tests with coverage"
	@echo "  make lint          Run linting"
	@echo "  make format        Format Python code"
	@echo "  make clean         Remove generated files"
	@echo "  make docker-up     Start Docker services"
	@echo "  make docker-down   Stop Docker services"
	@echo "  make docker-logs   View Docker logs"
	@echo "  make db-migrate    Run database migrations"
	@echo "  make db-revision   Create database migration"
