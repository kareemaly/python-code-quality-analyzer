#!/bin/bash

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$SCRIPT_DIR/release/utils.sh"

# Setup error handling
setup_error_handling

# Source all release scripts
source "$SCRIPT_DIR/release/validate.sh"
source "$SCRIPT_DIR/release/version.sh"
source "$SCRIPT_DIR/release/build.sh"
source "$SCRIPT_DIR/release/publish.sh"
source "$SCRIPT_DIR/release/git.sh"

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

# Main release process
function main() {
    log_info "Starting release process..."
    
    # Step 1: Validate environment and requirements
    validate_all
    
    # Step 2: Get new version
    new_version=$(bump_version "$bump_type")
    
    # Step 3: Update version files
    update_version_files "$new_version"
    verify_version_consistency
    
    # Step 4: Build package
    build_all
    
    # Step 5: Git operations
    git_release "$new_version" "$commit_title" "$commit_details"
    
    # Step 6: Publish to PyPI
    publish_all "$new_version"
    
    log_success "Release process completed successfully!"
    log_info "Version $new_version has been released"
}

# Execute main function
main 