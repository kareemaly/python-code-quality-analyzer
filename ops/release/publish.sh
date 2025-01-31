#!/bin/bash

# Source utilities
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$SCRIPT_DIR/utils.sh"

# Setup error handling
setup_error_handling

function publish_to_pypi() {
    log_info "Publishing to PyPI..."
    cd "$PROJECT_ROOT"
    
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

function verify_published_package() {
    local version=$1
    if [ -z "$version" ]; then
        log_error "Version not specified for verification"
        exit 1
    fi
    
    log_info "Verifying package publication..."
    cd "$PROJECT_ROOT"
    
    local timeout=60
    local interval=5
    local elapsed=0
    
    while [ $elapsed -lt $timeout ]; do
        if pip index versions "$PYPI_PACKAGE_NAME" | grep -q "$version"; then
            log_success "Package version $version verified on PyPI"
            return 0
        fi
        log_info "Waiting for package to appear on PyPI... (${elapsed}s/${timeout}s)"
        sleep $interval
        elapsed=$((elapsed + interval))
    done
    
    log_error "Timeout waiting for package to appear on PyPI"
    log_info "Available versions:"
    pip index versions "$PYPI_PACKAGE_NAME"
    exit 1
}

# Main publish function
function publish_all() {
    local version=$1
    if [ -z "$version" ]; then
        log_error "Version not specified for publishing"
        exit 1
    fi
    
    publish_to_pypi
    verify_published_package "$version"
    log_success "Publishing process completed successfully"
} 