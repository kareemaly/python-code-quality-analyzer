#!/bin/bash

# Detect shell and source appropriate config
if [ -n "$ZSH_VERSION" ]; then
    source ~/.zshrc 2>/dev/null || true
elif [ -n "$BASH_VERSION" ]; then
    source ~/.bashrc 2>/dev/null || true
fi

# Validate environment variables
if [ -z "$PIP_PUBLISH_API_TOKEN" ]; then
    echo "Error: PIP_PUBLISH_API_TOKEN environment variable is not set"
    exit 1
fi

# Help function
function show_help {
    echo "Usage: ./release.sh -t <commit_title> -d <commit_details> -b <bump_type>"
    echo "Options:"
    echo "  -t <commit_title>    Title for the commit message"
    echo "  -d <commit_details>  Details for the commit message"
    echo "  -b <bump_type>      Version bump type (major, minor, patch)"
    echo "  -h                   Show this help message"
    exit 1
}

# Parse arguments
while getopts "t:d:b:h" opt; do
    case $opt in
        t) commit_title="$OPTARG";;
        d) commit_details="$OPTARG";;
        b) bump_type="$OPTARG";;
        h) show_help;;
        \?) echo "Invalid option -$OPTARG" >&2; show_help;;
    esac
done

# Validate required arguments
if [ -z "$commit_title" ] || [ -z "$commit_details" ] || [ -z "$bump_type" ]; then
    echo "Error: Missing required arguments"
    show_help
fi

# Validate bump type
if [ "$bump_type" != "major" ] && [ "$bump_type" != "minor" ] && [ "$bump_type" != "patch" ]; then
    echo "Error: Invalid bump type. Must be major, minor, or patch"
    exit 1
fi

# Function to bump version
function bump_version {
    local current_version=$(grep 'version = ' pyproject.toml | head -1 | cut -d'"' -f2)
    if [[ ! "$current_version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        current_version="0.1.0"
    fi
    
    local major=$(echo $current_version | cut -d. -f1)
    local minor=$(echo $current_version | cut -d. -f2)
    local patch=$(echo $current_version | cut -d. -f3)

    case $bump_type in
        major) major=$((major + 1)); minor=0; patch=0;;
        minor) minor=$((minor + 1)); patch=0;;
        patch) patch=$((patch + 1));;
    esac

    local new_version="$major.$minor.$patch"
    echo $new_version
}

# Function to update version in files
function update_version_files {
    local new_version=$1
    sed -i '' "s/version=\".*\"/version=\"$new_version\"/" setup.py
    sed -i '' "s/version = \".*\"/version = \"$new_version\"/" pyproject.toml
}

# Function to clean build artifacts
function clean_build_artifacts {
    echo "Cleaning build artifacts..."
    rm -rf dist/ build/ *.egg-info/
}

# Function to build and check distribution
function build_and_check_dist {
    echo "Building distribution packages..."
    python -m build
    
    echo "Checking distribution packages..."
    twine check dist/*
}

# Function to create git commit and tag
function create_git_commit_and_tag {
    local new_version=$1
    echo "Creating git commit and tag..."
    
    # Remove existing tag if it exists
    git tag -d "v$new_version" 2>/dev/null || true
    git push origin ":refs/tags/v$new_version" 2>/dev/null || true
    
    # Create new commit and tag
    git add setup.py pyproject.toml
    git commit -m "$commit_title

$commit_details"
    git tag -a "v$new_version" -m "Version $new_version"
}

# Function to test package in Docker
function test_in_docker {
    local version=$1
    echo "Testing package in Docker..."
    
    # Make the test script executable
    chmod +x run_docker_tests.sh
    
    # Run the test script
    ./run_docker_tests.sh -v $version
    
    if [ $? -ne 0 ]; then
        echo "Docker tests failed!"
        exit 1
    fi
}

# Function to publish to PyPI
function publish_to_pypi {
    echo "Publishing to PyPI..."
    TWINE_USERNAME=__token__ TWINE_PASSWORD="$PIP_PUBLISH_API_TOKEN" python -m twine upload dist/*
}

# Main execution
echo "Starting release process..."

# Analyze current versions
echo -e "\nAnalyzing current versions before release..."
./analyze_versions.sh

# Activate virtual environment and install required packages
source .venv/bin/activate
python -m pip install --upgrade pip build twine

# Clean build artifacts
clean_build_artifacts

# Get new version
new_version=$(bump_version)

# Update version in files
update_version_files $new_version

# Build and check distribution
build_and_check_dist

# Test package in Docker
test_in_docker $new_version

# Create git commit and tag
create_git_commit_and_tag $new_version

# Publish to PyPI
publish_to_pypi

# Analyze updated versions
echo -e "\nAnalyzing versions after release..."
./analyze_versions.sh

echo "Release process completed successfully!"