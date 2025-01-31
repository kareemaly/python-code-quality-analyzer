"""
Base analyzer for code analysis
"""

import sys
from pathlib import Path
from typing import Any, Dict, Optional

from rich.console import Console


class BaseAnalyzer:
    """Base class for code analyzers."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the analyzer.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {
            "analysis": {
                "exclude_patterns": [],
                "dead_code": {"enabled": True},
                "similarity": {"enabled": True}
            },
            "output": {
                "verbose": False
            }
        }
        self.error_console = Console(file=sys.stderr)

    def _log_error(self, message: str) -> None:
        """Log an error message.
        
        Args:
            message: Error message to log
        """
        if self.config.get("output", {}).get("verbose", False):
            self.error_console.print(f"[red]Error:[/red] {message}")

    def should_ignore_file(self, file_path: Path) -> bool:
        """Check if a file should be ignored.
        
        Args:
            file_path: Path to check
            
        Returns:
            bool: True if the file should be ignored
        """
        exclude_patterns = self.config.get("analysis", {}).get("exclude_patterns", [])
        return any(pattern in str(file_path) for pattern in exclude_patterns)
