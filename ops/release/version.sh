#!/bin/bash

# Source utilities
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$SCRIPT_DIR/utils.sh"

# Setup error handling
setup_error_handling

function get_current_version() {
    local current_version=$(grep 'version = ' "$PYPROJECT_FILE" | head -1 | cut -d'"' -f2)
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
    
    log_info "Calculating new version..."
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
    if ! sed -i.bak "s/version=\"[^\"]*\"/version=\"$new_version\"/" setup.py; then
        log_error "Failed to update version in setup.py"
        exit 1
    fi
    rm -f setup.py.bak
    
    # Update pyproject.toml
    if ! sed -i.bak "s/version = \"[^\"]*\"/version = \"$new_version\"/" pyproject.toml; then
        log_error "Failed to update version in pyproject.toml"
        exit 1
    fi
    rm -f pyproject.toml.bak
    
    log_success "Version updated in all files"
}

function verify_version_consistency() {
    log_info "Verifying version consistency..."
    cd "$PROJECT_ROOT"
    
    local pyproject_version=$(grep 'version = ' "$PYPROJECT_FILE" | head -1 | cut -d'"' -f2)
    local setup_version=$(grep 'version=' "$SETUP_FILE" | head -1 | cut -d'"' -f2)
    
    if [ "$pyproject_version" != "$setup_version" ]; then
        log_error "Version mismatch: pyproject.toml ($pyproject_version) != setup.py ($setup_version)"
        exit 1
    fi
    
    log_success "Versions are consistent: $pyproject_version"
    echo "$pyproject_version"
} 