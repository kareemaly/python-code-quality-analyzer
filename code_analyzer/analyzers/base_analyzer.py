"""
Base analyzer interface
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional, Set, List
from fnmatch import fnmatch

from ..config.config_loader import Config

class BaseAnalyzer(ABC):
    """Base class for all analyzers"""
    
    # Common patterns to ignore during analysis
    IGNORED_PATTERNS: Set[str] = {
        # Virtual environments
        '.venv', 'venv', 'env', 'virtualenv',
        # Package management
        'node_modules', 'site-packages', '.tox', 'eggs', '.eggs',
        # Build and distribution
        'build', 'dist', '*.egg-info',
        # Cache directories
        '__pycache__', '.mypy_cache', '.pytest_cache', '.coverage',
        # Version control
        '.git', '.hg', '.svn',
        # IDE and editor files
        '.idea', '.vscode',
        # Test directories
        'tests', 'test', 'testing',
        # Documentation
        'docs', 'doc',
    }
    
    # File patterns to ignore
    IGNORED_FILE_PATTERNS: Set[str] = {
        # Test files
        'test_*.py', '*_test.py', '*_tests.py',
        # Setup and configuration
        'setup.py', 'conf.py', 'conftest.py',
        # Migration files
        '**/migrations/*.py',
        # Init files
        '__init__.py',
    }
    
    def __init__(self, config: Optional[Config] = None, config_root: Optional[Path] = None):
        """Initialize the analyzer.
        
        Args:
            config (Optional[Config]): Configuration object
            config_root (Optional[Path]): Path to configuration directory
        """
        self.config = config
        self.config_root = config_root
        self._validate_paths()
        self._metrics: Dict[str, Any] = {}
    
    @abstractmethod
    def analyze(self) -> Dict[str, Any]:
        """Run analysis and return results.
        
        Returns:
            Dict[str, Any]: Analysis results
        """
        pass
    
    @abstractmethod
    def _process_file(self, file_path: Path) -> Dict[str, Any]:
        """Process a single file and return its metrics.
        
        Args:
            file_path (Path): Path to the file to analyze
            
        Returns:
            Dict[str, Any]: The file's metrics
        """
        pass
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get the current metrics.
        
        Returns:
            Dict[str, Any]: The current metrics
        """
        return self._metrics
    
    def _is_python_file(self, file_path: Path) -> bool:
        """Check if file is a Python file."""
        return file_path.suffix == '.py'
    
    def _get_relative_path(self, file_path: Path) -> Optional[Path]:
        """Get path relative to current directory."""
        try:
            return file_path.resolve().relative_to(Path.cwd())
        except ValueError:
            return None
    
    def _matches_ignored_pattern(self, part: str) -> bool:
        """Check if a path part matches any ignored pattern."""
        if not self.config:
            return any(fnmatch(part, pattern) for pattern in self.IGNORED_PATTERNS)
        
        # Check both directory and file patterns from config
        patterns = set(self.config.analysis.exclude_patterns)
        # Add default patterns if not overridden
        if not patterns:
            patterns = self.IGNORED_PATTERNS
        
        return any(fnmatch(part, pattern) for pattern in patterns)
    
    def _matches_file_pattern(self, file_path: Path, pattern: str) -> bool:
        """Check if file matches a specific pattern."""
        path_str = str(file_path)
        return fnmatch(path_str, pattern)
    
    def _should_process_file(self, file_path: Path) -> bool:
        """Check if a file should be processed.
        
        Args:
            file_path (Path): Path to the file
            
        Returns:
            bool: True if the file should be processed
        """
        if not self._is_python_file(file_path):
            return False
            
        rel_path = self._get_relative_path(file_path)
        if not rel_path:
            return False
            
        # Check directory patterns
        if any(self._matches_ignored_pattern(part) for part in rel_path.parts):
            return False
            
        # Check file patterns
        patterns = (
            self.config.analysis.exclude_patterns
            if self.config
            else self.IGNORED_FILE_PATTERNS
        )
        if any(self._matches_file_pattern(rel_path, pattern) for pattern in patterns):
            return False
        
        return True
    
    def _validate_paths(self) -> None:
        """Validate required paths exist"""
        if not self.config_root or not self.config_root.exists():
            return
    
    def _read_json_file(self, path: Path) -> Dict[str, Any]:
        """Safely read and parse JSON file"""
        try:
            if path.exists():
                import json
                with open(path) as f:
                    return json.load(f)
        except Exception as e:
            raise ValueError(f"Error reading {path}: {e}")
        return {} 