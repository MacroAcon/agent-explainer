.PHONY: install format lint test unit-tests integration-tests run-failed-tests coverage clean help

# Default target
all: help

# Help output
help:
	@echo "CalCon Supplier Agent System Makefile"
	@echo ""
	@echo "Usage:"
	@echo "  make install           Install dependencies"
	@echo "  make format            Format code using black"
	@echo "  make lint              Lint code using pylint"
	@echo "  make test              Run all tests"
	@echo "  make unit-tests        Run unit tests only"
	@echo "  make integration-tests Run integration tests only"
	@echo "  make run-failed-tests  Run only failed tests from last run"
	@echo "  make coverage          Run tests with coverage report"
	@echo "  make clean             Clean up Python cache files and build artifacts"
	@echo ""

# Install dependencies
install:
	pip install -r requirements.txt

# Format code using black
format:
	black .

# Lint code using pylint
lint:
	pylint src/ tests/

# Run all tests
test:
	pytest

# Run unit tests only
unit-tests:
	pytest tests/test_*.py

# Run integration tests only
integration-tests:
	pytest tests/integration/

# Run only failed tests from the last run
run-failed-tests:
	pytest --last-failed

# Run tests with coverage
coverage:
	pytest --cov=src

# Clean up cache files and build artifacts
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .coverage -exec rm -rf {} +
	find . -type d -name htmlcov -exec rm -rf {} +
	find . -type d -name *.egg-info -exec rm -rf {} +
	find . -type d -name .eggs -exec rm -rf {} +
	find . -type d -name build -exec rm -rf {} +
	find . -type d -name dist -exec rm -rf {} + 