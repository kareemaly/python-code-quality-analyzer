"""
Base command class for CLI commands
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pathlib import Path
from rich.console import Console

from ..analyzers.base_analyzer import BaseAnalyzer
from ..formatters.base_formatter import BaseFormatter

class BaseCommand(ABC):
    """Base class for all CLI commands"""
    
    def __init__(self):
        self.console = Console()
        self.config_root: Optional[Path] = None
        self.analyzer: Optional[BaseAnalyzer] = None
        self.formatter: Optional[BaseFormatter] = None
    
    @abstractmethod
    def run(self, **kwargs) -> None:
        """Run the command with given arguments"""
        pass
    
    def _setup(self, config_root: Optional[Path] = None) -> None:
        """Set up command dependencies"""
        if config_root:
            self.config_root = config_root
        else:
            self.config_root = Path.home() / "Library/Application Support/Cursor"
    
    def _validate_setup(self) -> None:
        """Validate command setup"""
        if not self.analyzer:
            raise ValueError("Analyzer not set")
        if not self.formatter:
            raise ValueError("Formatter not set")
        if not self.config_root:
            raise ValueError("Config root not set")
    
    def _handle_error(self, error: Exception) -> None:
        """Handle command execution error"""
        self.console.print(f"[red]Error: {str(error)}[/red]")
    
    def _print_success(self, message: str) -> None:
        """Print success message"""
        self.console.print(f"[green]{message}[/green]")
    
    def _print_warning(self, message: str) -> None:
        """Print warning message"""
        self.console.print(f"[yellow]{message}[/yellow]")
    
    def _print_info(self, message: str) -> None:
        """Print info message"""
        self.console.print(f"[blue]{message}[/blue]") 