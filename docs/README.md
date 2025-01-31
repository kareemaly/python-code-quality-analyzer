# Code Analyzer

A Python tool for analyzing code complexity and quality metrics.

## Features

- Cyclomatic complexity analysis
- Maintainability index calculation
- Halstead metrics
- Function-level analysis
- Multiple output formats (console, JSON, CSV)
- Configurable thresholds and exclusions
- Rich console output with color-coded metrics

## Installation

```bash
pip install code-analyzer
```

## Usage

```bash
# Basic analysis of current directory
code-analyzer analyze

# Analyze specific directory
code-analyzer analyze src/

# Output in JSON format
code-analyzer analyze -f json

# Output in CSV format
code-analyzer analyze -f csv

# Exclude test files
code-analyzer analyze -e "*.test.py"

# Set minimum complexity threshold
code-analyzer analyze --min-complexity 7

# Enable verbose output
code-analyzer analyze -v
```

## Configuration

The analyzer can be configured using a YAML configuration file. Create a file named `.code-analyzer.yaml` in your project root:

```yaml
analysis:
  min_complexity: 5
  exclude_patterns:
    - "**/*.test.py"
    - "**/test_*.py"
    - "**/tests/**"

output:
  format: "console"
  show_progress: true
  verbose: false
  color: true

thresholds:
  complexity:
    low: 4
    medium: 7
    high: 10
  maintainability_index:
    high: 80
    medium: 60
    low: 40
```

## Output Formats

### Console Output

The default console output provides:
- Summary metrics (total files, functions, average complexity)
- List of complex functions above threshold
- Color-coded metrics for easy identification of issues
- Progress bar during analysis

### JSON Output

JSON output includes detailed metrics for each file:
- File path
- Cyclomatic complexity
- Maintainability index
- Function-level metrics
- Halstead metrics

### CSV Output

CSV output provides function-level metrics in a tabular format:
- File path
- Function name
- Complexity
- Line number
- Maintainability index

## Contributing

See [CONTRIBUTING.md](guides/CONTRIBUTING.md) for guidelines on contributing to this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 