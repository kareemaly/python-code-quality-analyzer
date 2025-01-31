#!/bin/bash
set -e

echo "Running unit tests..."

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Install test dependencies
pip install -e ".[test]" pytest pytest-cov

# Run tests with coverage
pytest tests/ --cov=code_analyzer --cov-report=html --cov-report=term-missing

echo "✅ Unit tests completed successfully" 