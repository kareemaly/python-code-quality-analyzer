#!/bin/bash
set -e

echo "Running Docker tests..."

# Build test image
docker build -t code-analyzer-test -f Dockerfile.test .

# Run tests in container
docker run --rm code-analyzer-test pytest tests/

echo "✅ Docker tests completed successfully" 