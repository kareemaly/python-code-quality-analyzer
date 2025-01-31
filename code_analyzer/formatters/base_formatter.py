"""
Base formatter class for output formatting
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree

class BaseFormatter(ABC):
    """Base class for all formatters"""
    
    def __init__(self):
        self.console = Console()
    
    @abstractmethod
    def format(self, data: Dict[str, Any]) -> Any:
        """Format data for output"""
        pass
    
    def _create_table(
        self,
        title: str,
        columns: list[str],
        column_styles: Optional[list[str]] = None
    ) -> Table:
        """Create a styled table"""
        table = Table(title=title, show_header=True, header_style="bold")
        for i, column in enumerate(columns):
            style = column_styles[i] if column_styles and i < len(column_styles) else None
            table.add_column(column, style=style)
        return table
    
    def _create_tree(self, title: str) -> Tree:
        """Create a styled tree"""
        return Tree(f"[bold]{title}[/bold]")
    
    def _create_panel(self, content: str, title: str) -> Panel:
        """Create a styled panel"""
        return Panel(content, title=title)
    
    def _format_number(self, value: float, precision: int = 2) -> str:
        """Format number with specified precision"""
        return f"{value:.{precision}f}"
    
    def _format_bytes(self, bytes: int) -> str:
        """Format bytes into human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes < 1024:
                return f"{bytes:.1f} {unit}"
            bytes /= 1024
        return f"{bytes:.1f} TB"
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in seconds to human readable format"""
        if seconds < 60:
            return f"{seconds:.1f}s"
        minutes = seconds / 60
        if minutes < 60:
            return f"{minutes:.1f}m"
        hours = minutes / 60
        return f"{hours:.1f}h" 