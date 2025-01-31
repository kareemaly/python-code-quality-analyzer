#!/bin/bash

# Source utilities
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$SCRIPT_DIR/utils.sh"

# Setup error handling
setup_error_handling

function create_release_branch() {
    local version=$1
    if [ -z "$version" ]; then
        log_error "Version not specified for release branch"
        exit 1
    fi
    
    log_info "Creating release branch..."
    cd "$PROJECT_ROOT"
    
    local branch_name="release/v$version"
    
    # Create and switch to release branch
    if ! git checkout -b "$branch_name"; then
        log_error "Failed to create release branch: $branch_name"
        exit 1
    fi
    
    log_success "Created and switched to release branch: $branch_name"
}

function commit_version_changes() {
    local version=$1
    local title=$2
    local details=$3
    
    if [ -z "$version" ] || [ -z "$title" ] || [ -z "$details" ]; then
        log_error "Missing required parameters for commit"
        exit 1
    fi
    
    log_info "Committing version changes..."
    cd "$PROJECT_ROOT"
    
    # Stage version files
    if ! git add "$PYPROJECT_FILE" "$SETUP_FILE" "$CHANGELOG_FILE"; then
        log_error "Failed to stage files"
        exit 1
    fi
    
    # Create commit
    if ! git commit -m "$title

$details"; then
        log_error "Failed to create commit"
        exit 1
    fi
    
    log_success "Changes committed successfully"
}

function create_version_tag() {
    local version=$1
    if [ -z "$version" ]; then
        log_error "Version not specified for tag"
        exit 1
    fi
    
    log_info "Creating version tag..."
    cd "$PROJECT_ROOT"
    
    # Remove existing tag if it exists
    git tag -d "v$version" 2>/dev/null || true
    git push origin ":refs/tags/v$version" 2>/dev/null || true
    
    # Create new tag
    if ! git tag -a "v$version" -m "Version $version"; then
        log_error "Failed to create tag"
        exit 1
    fi
    
    log_success "Version tag created: v$version"
}

function push_changes() {
    local version=$1
    if [ -z "$version" ]; then
        log_error "Version not specified for push"
        exit 1
    fi
    
    log_info "Pushing changes to remote..."
    cd "$PROJECT_ROOT"
    
    # Push branch
    if ! git push origin "$(git rev-parse --abbrev-ref HEAD)"; then
        log_error "Failed to push branch"
        exit 1
    fi
    
    # Push tag
    if ! git push origin "v$version"; then
        log_error "Failed to push tag"
        exit 1
    fi
    
    log_success "Changes pushed successfully"
}

# Main git operations function
function git_release() {
    local version=$1
    local title=$2
    local details=$3
    
    if [ -z "$version" ] || [ -z "$title" ] || [ -z "$details" ]; then
        log_error "Missing required parameters for git release"
        exit 1
    fi
    
    create_release_branch "$version"
    commit_version_changes "$version" "$title" "$details"
    create_version_tag "$version"
    push_changes "$version"
    log_success "Git release process completed successfully"
} 