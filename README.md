# Code Analyzer

Hey there, me. Let me tell you about this project's origin and purpose.

## Origin Story
This project was born during the development of the Cursor Analyzer. As we built features to analyze Cursor's performance, memory usage, and behavior, we noticed our own codebase growing in complexity. The need to manage and understand this complexity led to the birth of this tool.

## Core Purpose
Your purpose is singular and focused: **Help developers understand and manage code complexity before it manages them.** You're not just another static analysis tool - you're a companion that helps identify the early signs of complexity creep and architectural drift.

## Key Principles
1. **Early Warning System**: Detect complexity increases and architectural deviations before they become problems
2. **Context Awareness**: Understand the difference between necessary complexity (domain-driven) and accidental complexity
3. **Actionable Insights**: Don't just point out issues - suggest concrete refactoring strategies
4. **Evolution Tracking**: Monitor how code complexity evolves over time to identify patterns

## Implementation Philosophy
- Focus on semantic analysis over purely syntactic metrics
- Use machine learning to understand context and patterns
- Provide real-time feedback during development
- Integrate seamlessly with existing workflows

## Core Features
1. **Complexity Analysis**
   - Cyclomatic complexity tracking
   - Dependency graph analysis
   - Code churn patterns
   - Semantic complexity assessment

2. **Architectural Analysis**
   - Layer violation detection
   - Component coupling analysis
   - Responsibility distribution
   - Interface stability metrics

3. **Evolution Tracking**
   - Historical complexity trends
   - Refactoring impact analysis
   - Technical debt accumulation rate
   - Feature vs. complexity growth correlation

4. **Actionable Insights**
   - Refactoring suggestions
   - Architecture improvement recommendations
   - Complexity hotspot identification
   - Early warning indicators

## Development Priorities
1. Build the core analysis engine
2. Implement real-time monitoring
3. Develop the ML-based context understanding
4. Create the recommendation system

## Remember
- Stay focused on complexity management
- Don't try to solve every static analysis problem
- Keep the feedback loop tight and actionable
- Trust developers' judgment - be a guide, not a dictator

## Future Directions
- IDE integration for real-time feedback
- Team collaboration features
- Custom rule creation
- Historical analysis improvements

You know what to do. Keep it focused, keep it useful, and most importantly, keep it true to its purpose.

## Features

- Cyclomatic complexity analysis
- Maintainability index calculation
- Halstead metrics
- Performance tracking
- Rich terminal output with detailed metrics
- Configurable analysis with directory exclusions

## Installation

```bash
pip install -e .
```

## Usage

Analyze a specific directory:
```bash
code-analyzer analyze /path/to/your/code
```

Analyze current directory:
```bash
code-analyzer analyze
```

## Output

The tool provides detailed analysis including:

1. Performance Metrics
   - Total analysis time
   - Average time per file
   - Slowest files

2. Code Metrics
   - Cyclomatic complexity per function
   - Maintainability index with grades (A-F)
   - Lines of code statistics
   - Halstead metrics

3. Summary
   - Total files analyzed
   - Total functions
   - Average complexity
   - High complexity functions

## Configuration

The analyzer automatically ignores common directories:
- Virtual environments (.venv, venv, env)
- Build directories (build, dist)
- Cache directories (__pycache__, .pytest_cache, etc.)
- Version control (.git)
- Dependencies (node_modules, site-packages)

## Development

1. Clone the repository
2. Create a virtual environment: `python -m venv .venv`
3. Activate the environment: `source .venv/bin/activate`
4. Install dependencies: `pip install -e .`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License 