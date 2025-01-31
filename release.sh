#!/bin/bash

# Default values
BUMP_TYPE="patch"
COMMIT_TITLE=""
COMMIT_DETAILS=""

# Help function
show_help() {
    echo "Usage: ./release.sh [options]"
    echo "Options:"
    echo "  -t, --title         Commit title (required)"
    echo "  -d, --details       Commit details (optional)"
    echo "  -b, --bump          Version bump type: major, minor, patch (default: patch)"
    echo "  -h, --help          Show this help message"
    echo ""
    echo "Example:"
    echo "  ./release.sh -t \"Add new feature\" -d \"Detailed description\" -b minor"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--title)
            COMMIT_TITLE="$2"
            shift 2
            ;;
        -d|--details)
            COMMIT_DETAILS="$2"
            shift 2
            ;;
        -b|--bump)
            BUMP_TYPE="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Validate required arguments
if [ -z "$COMMIT_TITLE" ]; then
    echo "Error: Commit title is required"
    show_help
    exit 1
fi

# Validate bump type
if [[ ! "$BUMP_TYPE" =~ ^(major|minor|patch)$ ]]; then
    echo "Error: Invalid bump type. Must be major, minor, or patch"
    exit 1
fi

# Function to bump version in files
bump_version() {
    local current_version=$(grep -E "version\s*=\s*['\"].*['\"]" setup.py | grep -oE "[0-9]+\.[0-9]+\.[0-9]+")
    local major=$(echo $current_version | cut -d. -f1)
    local minor=$(echo $current_version | cut -d. -f2)
    local patch=$(echo $current_version | cut -d. -f3)

    case $BUMP_TYPE in
        major)
            major=$((major + 1))
            minor=0
            patch=0
            ;;
        minor)
            minor=$((minor + 1))
            patch=0
            ;;
        patch)
            patch=$((patch + 1))
            ;;
    esac

    local new_version="$major.$minor.$patch"
    echo "Bumping version from $current_version to $new_version"

    # Update version in setup.py
    sed -i "" "s/version=\"$current_version\"/version=\"$new_version\"/" setup.py
    
    # Update version in pyproject.toml
    sed -i "" "s/version = \"$current_version\"/version = \"$new_version\"/" pyproject.toml
    
    echo $new_version
}

# Function to build and check distribution
build_and_check() {
    echo "Building distribution packages..."
    rm -rf dist/ build/ *.egg-info/
    python -m build || exit 1
    
    echo "Checking distribution packages..."
    python -m twine check dist/* || exit 1
}

# Function to create git commit and tag
create_git_commit() {
    local version=$1
    local commit_msg="$COMMIT_TITLE"
    
    if [ ! -z "$COMMIT_DETAILS" ]; then
        commit_msg="$commit_msg\n\n$COMMIT_DETAILS"
    fi
    
    echo "Creating git commit and tag..."
    git add setup.py pyproject.toml
    git commit -m "$commit_msg" || exit 1
    
    # Remove existing tag if it exists
    git tag -d "v$version" 2>/dev/null || true
    git push origin ":refs/tags/v$version" 2>/dev/null || true
    
    # Create new tag
    git tag -a "v$version" -m "$commit_msg" || exit 1
}

# Function to publish to PyPI
publish_to_pypi() {
    echo "Publishing to PyPI..."
    if [ -z "$PIP_PUBLISH_API_TOKEN" ]; then
        echo "Error: PIP_PUBLISH_API_TOKEN environment variable is not set"
        exit 1
    fi
    
    # Use API token for authentication
    TWINE_USERNAME=__token__ TWINE_PASSWORD="$PIP_PUBLISH_API_TOKEN" python -m twine upload dist/*
}

# Main execution
echo "Starting release process..."

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Ensure we have the latest pip and build tools
python -m pip install --upgrade pip build twine || exit 1

# Bump version
NEW_VERSION=$(bump_version)

# Build and check distribution
build_and_check

# Create git commit and tag
create_git_commit $NEW_VERSION

# Publish to PyPI
publish_to_pypi

echo "Release v$NEW_VERSION completed successfully!"
echo "Don't forget to push the changes and tags:"
echo "  git push origin main"
echo "  git push origin v$NEW_VERSION" 