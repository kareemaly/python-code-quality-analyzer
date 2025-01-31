#!/bin/bash

# Help function
function show_help {
    echo "Usage: ./run_docker_tests.sh -v <version>"
    echo "Options:"
    echo "  -v <version>    Version of python-code-quality-analyzer to test"
    echo "  -h             Show this help message"
    exit 1
}

# Parse arguments
while getopts "v:h" opt; do
    case $opt in
        v) version="$OPTARG";;
        h) show_help;;
        \?) echo "Invalid option -$OPTARG" >&2; show_help;;
    esac
done

# Validate required arguments
if [ -z "$version" ]; then
    echo "Error: Version is required"
    show_help
fi

echo "Testing python-code-quality-analyzer version $version..."

# Build the test Docker image
docker build -t code-analyzer-test -f Dockerfile.test .

# Run tests in Docker with the specified version
docker run --rm -e VERSION=$version code-analyzer-test

if [ $? -ne 0 ]; then
    echo "Docker tests failed!"
    exit 1
fi

echo "Docker tests completed successfully!" 