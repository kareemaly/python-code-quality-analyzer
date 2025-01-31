#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Timeout settings (in seconds)
PYPI_TIMEOUT=30
GIT_TIMEOUT=10

# Error handling
set -e
trap 'echo -e "${RED}Error: Command failed at line $LINENO${NC}"' ERR

# Logging function
log() {
    local level=$1
    local msg=$2
    local color=$NC
    
    case $level in
        "INFO") color=$BLUE;;
        "SUCCESS") color=$GREEN;;
        "WARN") color=$YELLOW;;
        "ERROR") color=$RED;;
    esac
    
    echo -e "${color}[$level] $msg${NC}"
}

# Function to run command with timeout
run_with_timeout() {
    local timeout=$1
    local cmd=$2
    local msg=$3
    local allow_fail=${4:-false}
    
    log "INFO" "Starting: $msg"
    
    # Run command with timeout
    if timeout $timeout bash -c "$cmd" 2>/dev/null; then
        return 0
    else
        local status=$?
        if [ $status -eq 124 ]; then
            log "WARN" "Timeout after ${timeout}s: $msg"
        elif [ "$allow_fail" = "true" ]; then
            log "WARN" "Command failed (allowed): $msg"
        else
            log "ERROR" "Command failed: $msg"
        fi
        return $status
    fi
}

# Function to check if we're in a git repository
is_git_repo() {
    if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

log "INFO" "Starting version analysis..."

# Get all published versions from PyPI
log "INFO" "Fetching PyPI versions..."
if ! run_with_timeout $PYPI_TIMEOUT "pip install pip-tools >/dev/null 2>&1" "Installing pip-tools" true; then
    log "WARN" "Failed to install pip-tools, skipping PyPI version check"
else
    echo -e "\n${GREEN}Published versions on PyPI:${NC}"
    if ! run_with_timeout $PYPI_TIMEOUT "pip-compile --extra=dev --dry-run 2>/dev/null | grep 'python-code-quality-analyzer=='" "Checking PyPI versions" true; then
        log "WARN" "No published versions found on PyPI"
    fi
fi

# Git operations
if is_git_repo; then
    # Get all git tags
    log "INFO" "Fetching git tags..."
    echo -e "\n${GREEN}Git tags and their commits:${NC}"
    if ! run_with_timeout $GIT_TIMEOUT "git for-each-ref --sort=taggerdate --format '%(refname:short) %(taggerdate:short) %(subject)' refs/tags" "Checking git tags" true; then
        log "WARN" "No git tags found or operation timed out"
    fi

    # Get latest commit info
    log "INFO" "Fetching latest commit info..."
    echo -e "\n${GREEN}Latest commit:${NC}"
    if ! run_with_timeout $GIT_TIMEOUT "git log -1 --pretty=format:'Hash: %h%nDate: %ad%nMessage: %s' --date=short" "Getting latest commit" true; then
        log "ERROR" "Failed to get latest commit info"
    fi

    # Check for uncommitted changes
    log "INFO" "Checking for uncommitted changes..."
    if ! git diff-index --quiet HEAD -- 2>/dev/null; then
        log "WARN" "There are uncommitted changes in the working directory"
    else
        log "SUCCESS" "Working directory is clean"
    fi
else
    log "WARN" "Not a git repository, skipping git operations"
fi

# Get current version from pyproject.toml
log "INFO" "Checking version in pyproject.toml..."
if CURRENT_VERSION=$(grep '^version = ' pyproject.toml 2>/dev/null | cut -d'"' -f2); then
    log "SUCCESS" "Current version in pyproject.toml: ${CURRENT_VERSION}"
else
    log "ERROR" "Failed to read version from pyproject.toml"
    CURRENT_VERSION="unknown"
fi

# Get current version from setup.py
log "INFO" "Checking version in setup.py..."
if SETUP_VERSION=$(grep 'version=' setup.py 2>/dev/null | cut -d'"' -f2); then
    log "SUCCESS" "Current version in setup.py: ${SETUP_VERSION}"
else
    log "ERROR" "Failed to read version from setup.py"
    SETUP_VERSION="unknown"
fi

# Check if versions match
if [ "$CURRENT_VERSION" != "unknown" ] && [ "$SETUP_VERSION" != "unknown" ]; then
    if [ "$CURRENT_VERSION" != "$SETUP_VERSION" ]; then
        log "WARN" "Version mismatch between pyproject.toml ($CURRENT_VERSION) and setup.py ($SETUP_VERSION)"
    else
        log "SUCCESS" "Versions match between files"
    fi
fi

log "SUCCESS" "Version analysis completed" 