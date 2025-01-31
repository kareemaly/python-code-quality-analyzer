#!/bin/bash

# Source utilities
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$SCRIPT_DIR/utils.sh"

# Setup error handling
setup_error_handling

function clean_build_artifacts() {
    log_info "Cleaning build artifacts..."
    cd "$PROJECT_ROOT"
    rm -rf dist/ build/ *.egg-info/
    log_success "Build artifacts cleaned"
}

function run_tests() {
    log_info "Running test suite..."
    cd "$PROJECT_ROOT"
    
    # Run unit tests
    log_info "Running unit tests..."
    if ! "$SCRIPT_DIR/../test/unit.sh"; then
        log_error "Unit tests failed"
        exit 1
    fi
    log_success "Unit tests passed"
    
    # Run quality tests
    log_info "Running quality tests..."
    if ! "$SCRIPT_DIR/../test/quality.sh"; then
        log_error "Quality tests failed"
        exit 1
    fi
    log_success "Quality tests passed"
}

function build_package() {
    log_info "Building distribution packages..."
    cd "$PROJECT_ROOT"
    
    # Build both wheel and sdist
    if ! python -m build; then
        log_error "Failed to build distribution packages"
        exit 1
    fi
    
    # Verify dist directory exists and contains files
    if [ ! -d "dist" ] || [ -z "$(ls -A dist)" ]; then
        log_error "Build failed: dist directory is empty or missing"
        exit 1
    fi
    
    log_success "Distribution packages built successfully"
}

function check_distribution() {
    log_info "Checking distribution packages..."
    cd "$PROJECT_ROOT"
    
    # Check all distribution files with twine
    if ! twine check dist/*; then
        log_error "Distribution package check failed"
        exit 1
    fi
    
    # Additional checks for expected files
    if ! ls dist/*.whl >/dev/null 2>&1; then
        log_error "Wheel distribution file not found"
        exit 1
    fi
    
    if ! ls dist/*.tar.gz >/dev/null 2>&1; then
        log_error "Source distribution file not found"
        exit 1
    fi
    
    log_success "Distribution packages verified"
}

function test_package() {
    local version=$1
    if [ -z "$version" ]; then
        log_error "Version not specified for package testing"
        exit 1
    fi
    
    log_info "Testing package in Docker..."
    cd "$PROJECT_ROOT"
    
    # Run package tests in Docker
    if ! "$SCRIPT_DIR/../test/docker.sh" -v "$version"; then
        log_error "Package tests in Docker failed"
        exit 1
    fi
    
    # Run package installation tests
    if ! "$SCRIPT_DIR/../test/package.sh" -v "$version"; then
        log_error "Package installation tests failed"
        exit 1
    fi
    
    log_success "Package tests passed"
}

# Main build function
function build_all() {
    local version=$1
    if [ -z "$version" ]; then
        log_error "Version not specified for build"
        exit 1
    fi
    
    run_tests
    clean_build_artifacts
    build_package
    check_distribution
    test_package "$version"
    log_success "Build process completed successfully"
} 