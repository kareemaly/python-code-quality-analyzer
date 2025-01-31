"""Command line interface."""

import logging
from typing import Optional

import click
from rich.console import Console
from rich.logging import RichHandler

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
log = logging.getLogger("python_code_quality_analyzer")

console = Console()

@click.group()
@click.version_option()
@click.option("--debug", is_flag=True, help="Enable debug logging")
def main(debug: bool):
    """CLI tool for Python Code Quality Analyzer."""
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        log.debug("Debug logging enabled")

if __name__ == "__main__":
    main()
