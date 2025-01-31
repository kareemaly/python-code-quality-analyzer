"""
Main entry point for code analyzer CLI
"""

import sys
from pathlib import Path
import click

from .commands.command_registry import registry
from .commands.analyze import AnalyzeCommand

# Register commands
registry.register("analyze", AnalyzeCommand)

@click.group()
def cli():
    """Code Analyzer CLI - Analyze Python code complexity and quality"""
    pass

@cli.command()
@click.argument('path', type=click.Path(exists=True), required=False)
def analyze(path=None):
    """Analyze code complexity and quality metrics"""
    try:
        cmd = registry.get_command("analyze")
        cmd.run(target_path=path)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    cli() 