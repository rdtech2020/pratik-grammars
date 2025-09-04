# Makefile for Pratik's Grammar Correction API

.PHONY: help install dev test lint format clean docs run build

# Default target
help:
	@echo "Available commands:"
	@echo "  install    - Install dependencies"
	@echo "  dev        - Start development server"
	@echo "  test       - Run tests"
	@echo "  lint       - Run linting"
	@echo "  format     - Format code"
	@echo "  clean      - Clean up files"
	@echo "  docs       - Generate documentation"
	@echo "  run        - Run production server"
	@echo "  build      - Build application"
	@echo "  db-create  - Create database tables"
	@echo "  create-admin - Create default admin user"
	@echo "  create-admin-custom - Create custom admin user"

# Install dependencies
install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

# Start development server
dev:
	@echo "Starting development server..."
	python main.py

# Run tests
test:
	@echo "Running tests..."
	pytest tests/ -v --cov=src --cov-report=html

# Run linting
lint:
	@echo "Running linting..."
	flake8 src/ tests/ --max-line-length=88 --ignore=E203,W503
	black --check src/ tests/
	isort --check-only src/ tests/

# Format code
format:
	@echo "Formatting code..."
	black src/ tests/
	isort src/ tests/

# Clean up files
clean:
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -f test_grammar.db

# Generate documentation
docs:
	@echo "Generating documentation..."
	mkdocs build

# Run production server
run:
	@echo "Starting production server..."
	uvicorn src.grammar_app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Build application
build:
	@echo "Building application..."
	python -m py_compile src/grammar_app/main.py
	@echo "Build successful!"

# Database operations
db-migrate:
	@echo "Running database migrations..."
	alembic upgrade head

db-create:
	@echo "Creating database tables..."
	python -c "from src.grammar_app.database import Base, engine; Base.metadata.create_all(bind=engine)"

# Admin operations
create-admin:
	@echo "Creating admin user..."
	python scripts/create_admin.py

create-admin-custom:
	@echo "Creating custom admin user..."
	@read -p "Enter admin email: " email; \
	read -p "Enter admin name: " name; \
	read -s -p "Enter admin password: " password; \
	echo; \
	ADMIN_EMAIL=$$email ADMIN_NAME=$$name ADMIN_PASSWORD=$$password python scripts/create_admin.py

# Model operations
test-models:
	@echo "Testing different grammar correction models..."
	python scripts/test_models.py

model-info:
	@echo "Current model information:"
	@python3 -c "from src.grammar_app.services import get_grammar_service; service = get_grammar_service(); print(service.get_model_info())"

# Model operations
download-model:
	@echo "Downloading AI model..."
	python scripts/train_grammar_model.py --download

# Docker operations
docker-build:
	@echo "Building Docker image..."
	docker build -t pratik-grammar-api .

docker-run:
	@echo "Running Docker container..."
	docker run -p 8000:8000 pratik-grammar-api

# Setup development environment
setup-dev: install db-create download-model create-admin
	@echo "Development environment setup complete!"

# Full test suite
test-full: lint test
	@echo "Full test suite completed!"
