#!/bin/bash

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
function log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
function log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
function log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
function log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Error handling
set -e  # Exit on error
trap 'log_error "An error occurred. Exiting..."; exit 1' ERR

# Detect shell and source appropriate config
if [ -n "$ZSH_VERSION" ]; then
    source ~/.zshrc 2>/dev/null || true
elif [ -n "$BASH_VERSION" ]; then
    source ~/.bashrc 2>/dev/null || true
fi

# Function to validate environment
function validate_environment {
    log_info "Validating environment..."
    
    # Check virtual environment
    if [[ -z "${VIRTUAL_ENV}" ]]; then
        log_error "Not running in a virtual environment"
        exit 1
    fi
    log_success "Virtual environment active: ${VIRTUAL_ENV}"
    
    # Check Python version
    python_version=$(python -V 2>&1)
    log_success "Python version: ${python_version}"
    
    # Check required environment variables
    if [ -z "$PIP_PUBLISH_API_TOKEN" ]; then
        log_error "PIP_PUBLISH_API_TOKEN environment variable is not set"
        exit 1
    fi
    log_success "PyPI token configured"
    
    # Validate pip and required tools
    log_info "Installing/upgrading required tools..."
    python -m pip install --upgrade pip build twine >/dev/null 2>&1 || {
        log_error "Failed to install/upgrade required tools"
        exit 1
    }
    log_success "Required tools installed/upgraded"
}

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
        \?) log_error "Invalid option -$OPTARG"; show_help;;
    esac
done

# Validate required arguments
if [ -z "$commit_title" ] || [ -z "$commit_details" ] || [ -z "$bump_type" ]; then
    log_error "Missing required arguments"
    show_help
fi

# Validate bump type
if [ "$bump_type" != "major" ] && [ "$bump_type" != "minor" ] && [ "$bump_type" != "patch" ]; then
    log_error "Invalid bump type. Must be major, minor, or patch"
    exit 1
fi

# Function to bump version
function bump_version {
    log_info "Calculating new version..."
    local current_version=$(grep 'version = ' pyproject.toml | head -1 | cut -d'"' -f2)
    if [[ ! "$current_version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        log_warn "Invalid current version format, defaulting to 0.1.0"
        current_version="0.1.0"
    fi
    
    local major=$(echo $current_version | cut -d. -f1)
    local minor=$(echo $current_version | cut -d. -f2)
    local patch=$(echo $current_version | cut -d. -f3)

    case $bump_type in
        major) 
            # For first major release, set to 1.0.0
            if [ "$major" -eq "0" ]; then
                major=1
            else
                major=$((major + 1))
            fi
            minor=0
            patch=0
            ;;
        minor) minor=$((minor + 1)); patch=0;;
        patch) patch=$((patch + 1));;
    esac

    local new_version="$major.$minor.$patch"
    log_success "Version bump: ${current_version} -> ${new_version}"
    echo $new_version
}

# Function to update version in files
function update_version_files {
    local new_version=$1
    log_info "Updating version in files..."
    
    # Update setup.py
    if ! sed -i '' "s/version=\".*\"/version=\"$new_version\"/" setup.py; then
        log_error "Failed to update version in setup.py"
        exit 1
    fi
    
    # Update pyproject.toml
    if ! sed -i '' "s/version = \".*\"/version = \"$new_version\"/" pyproject.toml; then
        log_error "Failed to update version in pyproject.toml"
        exit 1
    fi
    
    log_success "Version updated in all files"
}

# Function to clean build artifacts
function clean_build_artifacts {
    log_info "Cleaning build artifacts..."
    rm -rf dist/ build/ *.egg-info/
    log_success "Build artifacts cleaned"
}

# Function to build and check distribution
function build_and_check_dist {
    log_info "Building distribution packages..."
    if ! python -m build; then
        log_error "Failed to build distribution packages"
        exit 1
    fi
    
    log_info "Checking distribution packages..."
    if ! twine check dist/*; then
        log_error "Distribution package check failed"
        exit 1
    fi
    log_success "Distribution packages built and checked"
}

# Function to test package in Docker
function test_in_docker {
    local version=$1
    log_info "Testing package in Docker..."
    
    # Make the test script executable
    chmod +x run_docker_tests.sh
    
    # Run the test script with a timeout
    if ! timeout 300 ./run_docker_tests.sh -v $version; then
        log_error "Docker tests failed or timed out"
        exit 1
    fi
    log_success "Docker tests passed"
}

# Function to create git commit and tag
function create_git_commit_and_tag {
    local new_version=$1
    log_info "Creating git commit and tag..."
    
    # Check if we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log_error "Not a git repository"
        exit 1
    fi
    
    # Remove existing tag if it exists
    git tag -d "v$new_version" 2>/dev/null || true
    git push origin ":refs/tags/v$new_version" 2>/dev/null || true
    
    # Create new commit and tag
    if ! git add setup.py pyproject.toml; then
        log_error "Failed to stage files"
        exit 1
    fi
    
    if ! git commit -m "$commit_title

$commit_details"; then
        log_error "Failed to create commit"
        exit 1
    fi
    
    if ! git tag -a "v$new_version" -m "Version $new_version"; then
        log_error "Failed to create tag"
        exit 1
    fi
    log_success "Git commit and tag created"
}

# Function to publish to PyPI
function publish_to_pypi {
    log_info "Publishing to PyPI..."
    local max_retries=3
    local retry_count=0
    local wait_time=5
    
    while [ $retry_count -lt $max_retries ]; do
        if TWINE_USERNAME=__token__ TWINE_PASSWORD="$PIP_PUBLISH_API_TOKEN" python -m twine upload dist/* --verbose; then
            log_success "Successfully published to PyPI"
            return 0
        fi
        
        retry_count=$((retry_count + 1))
        if [ $retry_count -lt $max_retries ]; then
            log_warn "Upload failed, retrying in ${wait_time} seconds... (Attempt ${retry_count}/${max_retries})"
            sleep $wait_time
            wait_time=$((wait_time * 2))
        fi
    done
    
    log_error "Failed to publish to PyPI after ${max_retries} attempts"
    exit 1
}

# Function to verify published package
function verify_published_package {
    local version=$1
    local timeout=60
    local interval=5
    local elapsed=0
    
    log_info "Verifying package publication..."
    while [ $elapsed -lt $timeout ]; do
        if pip index versions python-code-quality-analyzer | grep -q "$version"; then
            log_success "Package version $version verified on PyPI"
            return 0
        fi
        log_info "Waiting for package to appear on PyPI... (${elapsed}s/${timeout}s)"
        sleep $interval
        elapsed=$((elapsed + interval))
    done
    
    log_error "Timeout waiting for package to appear on PyPI"
    log_info "Available versions:"
    pip index versions python-code-quality-analyzer
    exit 1
}

# Main execution
log_info "Starting release process..."

# Validate environment
validate_environment

# Analyze current versions
log_info "Analyzing current versions before release..."
./analyze_versions.sh

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

# Verify publication
verify_published_package $new_version

# Analyze updated versions
log_info "Analyzing versions after release..."
./analyze_versions.sh

log_success "Release process completed successfully!"