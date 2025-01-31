#!/bin/bash

# Source utilities
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$SCRIPT_DIR/utils.sh"

# Setup error handling
setup_error_handling

function get_current_version() {
    # Extract version without color codes
    local current_version=$(grep -o 'version = "[^"]*"' "$PYPROJECT_FILE" | head -1 | cut -d'"' -f2)
    if [[ ! "$current_version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        log_warn "Invalid current version format in $PYPROJECT_FILE, defaulting to 0.1.0"
        current_version="0.1.0"
    fi
    echo "$current_version"
}

function bump_version() {
    local bump_type=$1
    if [ -z "$bump_type" ]; then
        log_error "Bump type not specified"
        exit 1
    fi
    
    local current_version=$(get_current_version)
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
        minor) 
            minor=$((minor + 1))
            patch=0
            ;;
        patch) 
            patch=$((patch + 1))
            ;;
        *)
            log_error "Invalid bump type: $bump_type. Must be major, minor, or patch"
            exit 1
            ;;
    esac

    local new_version="$major.$minor.$patch"
    log_info "Calculating new version..."
    log_success "Version bump: ${current_version} -> ${new_version}"
    echo "$new_version"
}

function update_version_files() {
    local new_version=$1
    if [ -z "$new_version" ]; then
        log_error "New version not specified"
        exit 1
    fi
    
    log_info "Updating version in files..."
    cd "$PROJECT_ROOT"
    
    # Update setup.py
    local setup_tmp=$(mktemp)
    sed "/^[[:space:]]*version=/c\    version=\"$new_version\"," setup.py > "$setup_tmp"
    if [ $? -eq 0 ]; then
        mv "$setup_tmp" setup.py
    else
        rm -f "$setup_tmp"
        log_error "Failed to update version in setup.py"
        exit 1
    fi
    
    # Update pyproject.toml
    local pyproject_tmp=$(mktemp)
    sed "/^version = /c\version = \"$new_version\"" pyproject.toml > "$pyproject_tmp"
    if [ $? -eq 0 ]; then
        mv "$pyproject_tmp" pyproject.toml
    else
        rm -f "$pyproject_tmp"
        log_error "Failed to update version in pyproject.toml"
        exit 1
    fi
    
    log_success "Version updated in all files"
}

function verify_version_consistency() {
    log_info "Verifying version consistency..."
    cd "$PROJECT_ROOT"
    
    # Extract versions without color codes
    local pyproject_version=$(grep -o 'version = "[^"]*"' "$PYPROJECT_FILE" | head -1 | cut -d'"' -f2)
    local setup_version=$(grep -o 'version="[^"]*"' "$SETUP_FILE" | head -1 | cut -d'"' -f2)
    
    if [ -z "$pyproject_version" ] || [ -z "$setup_version" ]; then
        log_error "Failed to extract version from one or both files"
        exit 1
    fi
    
    if [ "$pyproject_version" != "$setup_version" ]; then
        log_error "Version mismatch: pyproject.toml ($pyproject_version) != setup.py ($setup_version)"
        exit 1
    fi
    
    log_success "Versions are consistent: $pyproject_version"
    echo "$pyproject_version"
} 