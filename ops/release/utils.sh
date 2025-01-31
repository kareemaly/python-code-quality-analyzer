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

# Error handling setup
function setup_error_handling() {
    set -e  # Exit on error
    set -o pipefail  # Exit on pipe failures
    trap 'log_error "An error occurred on line $LINENO in $BASH_SOURCE. Exiting..."; exit 1' ERR
}

# Get script directory
RELEASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
OPS_DIR="$( cd "$RELEASE_DIR/.." && pwd )"
PROJECT_ROOT="$( cd "$OPS_DIR/.." && pwd )"

# Export common variables
export PYPI_PACKAGE_NAME="python-code-quality-analyzer"
export PYPROJECT_FILE="$PROJECT_ROOT/pyproject.toml"
export SETUP_FILE="$PROJECT_ROOT/setup.py"
export CHANGELOG_FILE="$PROJECT_ROOT/docs/CHANGELOG.md"
export OPS_DIR
export PROJECT_ROOT
export RELEASE_DIR 