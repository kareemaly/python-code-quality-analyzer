# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-31

### Added
- Version analysis script to track published versions and their commits
- Version analysis integration in release process
- Version consistency checks between setup.py and pyproject.toml
- Comprehensive test suite with Docker integration
- Improved error handling and logging throughout the codebase

### Changed
- Enhanced release process with better version tracking
- Improved release script organization
- Updated documentation to reflect new features
- Stabilized API and configuration handling
- Enhanced output formatting and display

### Fixed
- Configuration loader properly handles user config overrides
- JSON output handling prevents progress bar interference
- Verbose output formatting and display
- Complex functions display in metrics table
- Version consistency between configuration files

## [0.4.0] - 2024-01-31

Initial stable release with basic functionality.

## [0.2.6] - 2024-01-31

### Added
- Added version analysis script to track published versions and their commits
- Added version analysis to release process
- Added version consistency checks between setup.py and pyproject.toml

### Changed
- Enhanced release process with better version tracking
- Improved release script organization

## [0.2.5] - 2024-01-31

### Fixed
- Fixed configuration loader to properly handle user config overrides
- Fixed JSON output handling to prevent progress bar interference
- Fixed verbose output formatting and display
- Fixed "Total Files" metric to always appear first in performance table
- Fixed complex functions display in metrics table

### Changed
- Updated .gitignore to be more comprehensive
- Improved code organization and structure
- Enhanced test coverage and reliability

### Added
- Added proper error handling for configuration loading
- Added better progress bar management
- Added more detailed logging in verbose mode

## [0.2.4] - 2024-01-31

### Fixed
- Fixed configuration loader to properly handle user config overrides
- Fixed JSON output handling to prevent progress bar interference
- Fixed verbose output formatting and display
- Fixed "Total Files" metric to always appear first in performance table
- Fixed complex functions display in metrics table

### Changed
- Updated .gitignore to be more comprehensive
- Improved code organization and structure
- Enhanced test coverage and reliability

### Added
- Added proper error handling for configuration loading
- Added better progress bar management
- Added more detailed logging in verbose mode

## [0.2.3] - 2024-01-30

### Added
- Initial public release
- Basic code complexity analysis
- Support for multiple output formats (console, JSON, CSV)
- Configuration system with defaults and overrides
- Command-line interface with various options
- Progress tracking and verbose output
- Documentation and examples

[1.0.0]: https://github.com/kareemaly/python-code-quality-analyzer/compare/v0.4.0...v1.0.0
[0.4.0]: https://github.com/kareemaly/python-code-quality-analyzer/compare/v0.2.2...v0.4.0
[0.2.6]: https://github.com/kareemaly/python-code-quality-analyzer/compare/v0.2.5...v0.2.6
[0.2.5]: https://github.com/kareemaly/python-code-quality-analyzer/compare/v0.2.4...v0.2.5
[0.2.4]: https://github.com/kareemaly/python-code-quality-analyzer/compare/v0.2.3...v0.2.4
[0.2.3]: https://github.com/kareemaly/python-code-quality-analyzer/releases/tag/v0.2.3 