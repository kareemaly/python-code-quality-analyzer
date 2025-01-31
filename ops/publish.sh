#!/bin/bash
set -e

# Change to the repository root directory
cd "$(dirname "$0")/.."

echo "🚀 Starting publication process..."

# Run unit tests
echo "\n📋 Step 1: Running unit tests"
./ops/test_unit.sh

# Run quality checks
echo "\n📋 Step 2: Running code quality checks"
./ops/test_quality.sh

# Build and publish to PyPI
echo "\n📋 Step 3: Building and publishing package"
python -m build
python -m twine upload dist/*

# Run Docker tests after publish
echo "\n📋 Step 4: Running Docker tests"
./ops/test_docker.sh

echo "\n✨ Publication process completed successfully!" 