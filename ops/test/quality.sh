#!/bin/bash
set -e

echo "Running code quality checks..."

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Install quality check dependencies
pip install black isort pylint

# Run code quality checks
echo "Running Black formatter check..."
black --check .

echo "Running isort import check..."
isort --check-only .

echo "Running pylint..."
pylint code_analyzer/

echo "Running our own code analyzer..."
code-analyzer analyze code_analyzer/ --config code_analyzer/config/default_config.yaml

echo "✅ Code quality checks completed successfully" 