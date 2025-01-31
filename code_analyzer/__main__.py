"""
Main entry point for code analyzer CLI
"""

import sys
from pathlib import Path
import click
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn
from rich.console import Console

from .commands.command_registry import registry

# Global options
OUTPUT_FORMATS = ['console', 'json', 'csv']

@click.group()
@click.version_option(version='0.1.0')
def cli():
    """Code Analyzer CLI - Analyze Python code complexity and quality.
    
    This tool helps you understand and manage code complexity by providing:
    - Cyclomatic complexity metrics
    - Maintainability index
    - Halstead metrics
    - Function-level analysis
    """
    pass

@cli.command()
@click.argument('path', type=click.Path(exists=True), required=False)
@click.option('--format', '-f', type=click.Choice(OUTPUT_FORMATS), default='console',
              help='Output format (default: console)')
@click.option('--min-complexity', '-c', type=int, default=5,
              help='Minimum complexity to highlight (default: 5)')
@click.option('--exclude', '-e', multiple=True,
              help='Glob patterns to exclude (can be used multiple times)')
@click.option('--no-progress', is_flag=True,
              help='Disable progress bar')
@click.option('--verbose', '-v', is_flag=True,
              help='Enable verbose output')
@click.option('--config', type=click.Path(exists=True),
              help='Path to configuration file')
def analyze(path=None, format='console', min_complexity=5, exclude=None,
           no_progress=False, verbose=False, config=None):
    """Analyze code complexity and quality metrics.
    
    If PATH is not provided, analyzes the current directory.
    
    Examples:
        code-analyzer analyze                # Analyze current directory
        code-analyzer analyze src/           # Analyze src directory
        code-analyzer analyze -f json        # Output in JSON format
        code-analyzer analyze -e "*.test.py" # Exclude test files
    """
    console = Console()
    
    try:
        # Create command instance
        cmd = registry.get_command("analyze")
        
        # Set up progress tracking
        if not no_progress:
            with Progress(
                SpinnerColumn(),
                *Progress.get_default_columns(),
                TimeElapsedColumn(),
                console=console,
                transient=True
            ) as progress:
                progress.add_task("Analyzing...", total=None)
                result = cmd.run(
                    target_path=path,
                    output_format=format,
                    min_complexity=min_complexity,
                    exclude_patterns=exclude,
                    verbose=verbose,
                    config_path=config
                )
        else:
            result = cmd.run(
                target_path=path,
                output_format=format,
                min_complexity=min_complexity,
                exclude_patterns=exclude,
                verbose=verbose,
                config_path=config
            )
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]", err=True)
        if verbose:
            console.print_exception()
        sys.exit(1)

if __name__ == '__main__':
    cli() 