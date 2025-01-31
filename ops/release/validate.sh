#!/bin/bash

# Source utilities
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$SCRIPT_DIR/utils.sh"

# Setup error handling
setup_error_handling

function validate_environment() {
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

function validate_git_state() {
    log_info "Validating git state..."
    
    # Check if we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log_error "Not a git repository"
        exit 1
    fi
    
    # Check for uncommitted changes
    if ! git diff --quiet HEAD; then
        log_error "There are uncommitted changes in the working directory"
        exit 1
    fi
    
    log_success "Git state is clean"
}

function validate_files() {
    log_info "Validating required files..."
    
    # Check required files exist
    for file in "$PYPROJECT_FILE" "$SETUP_FILE" "$CHANGELOG_FILE"; do
        if [ ! -f "$file" ]; then
            log_error "Required file not found: $file"
            exit 1
        fi
    done
    
    log_success "All required files present"
}

# Main validation function
function validate_all() {
    validate_environment
    validate_git_state
    validate_files
    log_success "All validations passed"
} 