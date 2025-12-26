# Makefile for Train Booking API

.PHONY: install install-dev test lint format clean deploy destroy logs help

# Install production dependencies
install:
	pip install -r requirements.txt
	cd infrastructure && pip install -r requirements.txt

# Install development dependencies
install-dev: install
	pip install -r requirements-dev.txt

# Run tests
test:
	pytest tests/ -v --cov=app --cov-report=html --cov-report=term

# Run linter
lint:
	flake8 app/ bedrock_agent/ tests/
	mypy app/ bedrock_agent/

# Format code
format:
	black app/ bedrock_agent/ tests/ infrastructure/

# Clean build artifacts
clean:
	rm -rf __pycache__
	rm -rf **/__pycache__
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf cdk.out
	rm -rf .cdk.staging
	find . -type f -name "*.pyc" -delete

# Run locally
run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Build Docker image locally
docker-build:
	docker build -t train-booking-api .

# Run Docker container locally
docker-run: docker-build
	docker run -p 8000:8080 train-booking-api

# Deploy to AWS
deploy:
	cd infrastructure && cdk deploy --all

# Destroy AWS resources
destroy:
	cd infrastructure && cdk destroy --all

# View Lambda logs
logs:
	aws logs tail /aws/lambda/train-booking-api --follow

# View Agent logs
logs-agent:
	aws logs tail /aws/lambda/train-booking-action-group --follow

# Show help
help:
	@echo "Available commands:"
	@echo "  make install        - Install production dependencies"
	@echo "  make install-dev    - Install development dependencies"
	@echo "  make test           - Run tests"
	@echo "  make lint           - Run linters"
	@echo "  make format         - Format code"
	@echo "  make clean          - Clean build artifacts"
	@echo "  make run            - Run API locally"
	@echo "  make docker-build   - Build Docker image"
	@echo "  make docker-run     - Run Docker container"
	@echo "  make deploy         - Deploy to AWS"
	@echo "  make destroy        - Destroy AWS resources"
	@echo "  make logs           - View API Lambda logs"
	@echo "  make logs-agent     - View Agent Lambda logs"

