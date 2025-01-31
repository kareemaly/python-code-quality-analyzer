"""
Main entry point for code analyzer CLI
"""

import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console

from .commands.command_registry import registry
from .config.config_loader import ConfigError


@click.group()
@click.version_option(version="0.1.0")
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
@click.argument("paths", nargs=-1, type=click.Path(exists=True))
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    help="Path to configuration file",
)
@click.option(
    "--output",
    "-o",
    type=click.Choice(["console", "json", "csv"]),
    default="console",
    help="Output format",
)
@click.option(
    "--min-complexity",
    "-m",
    type=int,
    help="Minimum complexity to highlight",
)
@click.option(
    "--exclude",
    "-e",
    multiple=True,
    help="Glob patterns to exclude",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output",
)
def analyze(paths, config, output, min_complexity, exclude, verbose):
    """Analyze code complexity and quality."""
    error_console = Console(file=sys.stderr)
    
    try:
        # Create command instance with options
        cmd = registry.get_command(
            "analyze",
            config_path=config,
            verbose=verbose,
            output=output,
            min_complexity=min_complexity,
            exclude=exclude
        )
        
        if not cmd:
            raise click.ClickException("Analyze command not found")
            
        if not paths:
            paths = ["."]
            
        result = cmd.run(paths)
        if result != 0:
            raise click.ClickException("Analysis failed")
            
    except Exception as e:
        error_console.print(f"[red]Error:[/red] {str(e)}")
        if verbose:
            error_console.print_exception()
        raise click.Abort()


if __name__ == "__main__":
    cli()
