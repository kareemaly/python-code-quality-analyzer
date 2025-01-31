#!/bin/bash

set -e  # Exit on any error

echo "Starting package test..."

# Function to check if version exists on PyPI
function check_version_exists {
    pip index versions python-code-quality-analyzer | grep -q "Available versions: .*$VERSION"
    return $?
}

# Wait for package version with timeout
echo "Waiting for version $VERSION to be available on PyPI..."
TIMEOUT=60
INTERVAL=5
ELAPSED=0

while [ $ELAPSED -lt $TIMEOUT ]; do
    if check_version_exists; then
        echo "Version $VERSION found on PyPI!"
        break
    fi
    echo "Version $VERSION not found yet, waiting ${INTERVAL}s... (${ELAPSED}s/${TIMEOUT}s)"
    sleep $INTERVAL
    ELAPSED=$((ELAPSED + INTERVAL))
done

if [ $ELAPSED -ge $TIMEOUT ]; then
    echo "Timeout waiting for version $VERSION to appear on PyPI"
    echo "Available versions:"
    pip index versions python-code-quality-analyzer
    exit 1
fi

# Install the package
echo "Installing python-code-quality-analyzer..."
pip install python-code-quality-analyzer==$VERSION

# Create a test Python project
echo "Creating test Python project..."
mkdir -p test_project
cd test_project

cat > main.py << 'EOL'
def complex_function(a, b, c):
    if a > 0:
        if b > 0:
            if c > 0:
                return a + b + c
            else:
                return a + b
        else:
            return a
    return 0

def simple_function():
    return "Hello, World!"

if __name__ == "__main__":
    print(complex_function(1, 2, 3))
    print(simple_function())
EOL

# Test the analyzer on our test project
echo "Testing code-analyzer on test project..."
code-analyzer analyze .

echo "All tests completed successfully!" 