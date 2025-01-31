# Contributing to Python Code Quality Analyzer

Thank you for your interest in contributing to the Python Code Quality Analyzer! This document provides guidelines and instructions for contributing to the project.

## Getting Started

### Prerequisites
- Python 3.8 or higher
- pip and virtualenv
- Git

### Setting Up Development Environment
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/python-code-quality-analyzer.git
   cd python-code-quality-analyzer
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

## Development Workflow

### Branch Naming Convention
- Feature branches: `feature/description`
- Bug fixes: `fix/description`
- Documentation: `docs/description`
- Performance improvements: `perf/description`

### Commit Messages
Follow the conventional commits specification:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `test:` for test-related changes
- `refactor:` for code refactoring
- `style:` for formatting changes
- `perf:` for performance improvements

### Testing
- Write tests for new features
- Ensure all tests pass before submitting PR
- Maintain or improve code coverage
- Run tests using: `pytest`

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Add docstrings for public functions and classes
- Run linting: `flake8`

## Pull Request Process
1. Create a new branch from `main`
2. Make your changes
3. Update documentation if needed
4. Run tests and ensure they pass
5. Submit PR with clear description of changes
6. Wait for review and address feedback

## Release Process
1. Update version in `setup.py` and `pyproject.toml`
2. Update CHANGELOG.md
3. Create release PR
4. After merge, create GitHub release
5. Publish to PyPI using `release.sh`

## Getting Help
- Open an issue for questions
- Join our community discussions
- Check existing documentation

Thank you for contributing! 