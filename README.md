# Python Code Quality Analyzer

A powerful tool for analyzing Python code complexity, quality, and maintainability. Get insights into your codebase with detailed metrics and actionable recommendations for improvement.

## Features

- 📊 **Complexity Analysis**: Calculate cyclomatic complexity for functions and files
- 🎯 **Quality Metrics**: Measure maintainability index and identify problematic areas
- 🔍 **Detailed Reports**: Get comprehensive reports in console, JSON, or CSV format
- ⚡ **Fast & Efficient**: Analyze large codebases quickly with minimal overhead
- 🎨 **Beautiful Output**: Rich console output with tables and color-coding
- ⚙️ **Configurable**: Customize analysis with exclude patterns and complexity thresholds
- 📋 **Actionable Insights**: Clear recommendations for code improvement

## Installation

```bash
pip install python-code-quality-analyzer
```

## Quick Start

Analyze your current directory:
```bash
code-analyzer analyze .
```

Get detailed output with recommendations:
```bash
code-analyzer analyze . --verbose
```

Focus on highly complex code:
```bash
code-analyzer analyze . --min-complexity 10
```

Export analysis for further processing:
```bash
code-analyzer analyze . --format json > analysis.json
```

## Usage Examples

### Basic Analysis

```bash
code-analyzer analyze /path/to/your/project
```

This will:
1. Analyze all Python files in the directory
2. Calculate complexity metrics
3. Generate a detailed report with:
   - Overall project health metrics
   - Files that need attention
   - Specific recommendations for improvement
   - Dependency analysis
   - Maintainability scores

### Advanced Options

```bash
# Get detailed analysis with all metrics
code-analyzer analyze . --verbose

# Export as CSV for spreadsheet analysis
code-analyzer analyze . --format csv > analysis.csv

# Focus on highly complex functions
code-analyzer analyze . --min-complexity 10

# Exclude test files and vendor code
code-analyzer analyze . --exclude "**/tests/*" --exclude "**/vendor/*"

# Use custom configuration
code-analyzer analyze . --config myconfig.yaml
```

### Configuration File

Create a `code_analyzer_config.yaml` file:

```yaml
analysis:
  min_complexity: 5
  exclude_patterns:
    - "**/test_*.py"
    - "**/vendor/**"
    - "**/__init__.py"

output:
  format: console
  show_progress: true
  verbose: false
```

## Output Example

```
         Project Overview                                    
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Metric             ┃ Value ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ Total Files        │ 25    │
│ Total Functions    │ 150   │
│ Average Complexity │ 3.45  │
└────────────────────┴───────┘

         Code Quality                                    
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Metric             ┃ Value ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ Average MI         │ 65.42 │
│ Total Complexity   │ 517   │
└────────────────────┴───────┘

      Action Items
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ • High Priority:                                    ┃
┃   - Refactor cli.py (complexity: 202, MI: 0.0)     ┃
┃   - Split performance.py into smaller modules       ┃
┃                                                    ┃
┃ • Medium Priority:                                 ┃
┃   - Improve maintainability of history.py          ┃
┃   - Break down complex functions in ai.py          ┃
┃                                                    ┃
┃ • Consider:                                        ┃
┃   - Reducing dependencies in network.py            ┃
┃   - Adding documentation to low MI files           ┃
└────────────────────────────────────────────────────┘
```

## JSON Output Structure

The JSON output provides detailed metrics for programmatic analysis:

```json
{
  "summary": {
    "total_files": 25,
    "total_functions": 150,
    "average_complexity": 3.45,
    "average_maintainability": 65.42
  },
  "complex_files": [...],
  "low_maintainability_files": [...],
  "recommendations": [...],
  "detailed_metrics": {
    "file.py": {
      "complexity": 10,
      "maintainability": 65.4,
      "dependencies": [...],
      "functions": 5
    }
  }
}
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 