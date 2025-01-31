"""
Code complexity analyzer
"""

import ast
from pathlib import Path
from typing import Dict, Any, Optional, List
import os

from .base_analyzer import BaseAnalyzer
from ..metrics.complexity import ComplexityMetrics, ComplexityVisitor
from ..config.config_loader import Config

class ComplexityAnalyzer(BaseAnalyzer):
    """Analyzer for code complexity metrics"""
    
    def __init__(self, config: Optional[Config] = None, config_root: Optional[Path] = None):
        """Initialize the analyzer.
        
        Args:
            config (Optional[Config]): Configuration object
            config_root (Optional[Path]): Path to configuration directory
        """
        super().__init__(config_root)
        self.config = config
        self._metrics = self._create_empty_metrics()
        self.metrics_calculator = ComplexityMetrics()
    
    def _create_empty_metrics(self) -> Dict[str, Any]:
        """Create empty metrics dictionary."""
        return {
            "files": [],
            "total_complexity": 0,
            "average_complexity": 0,
            "total_functions": 0
        }
    
    def _reset_metrics(self) -> None:
        """Reset metrics to initial state."""
        self._metrics = self._create_empty_metrics()
    
    def _calculate_average_complexity(self) -> None:
        """Calculate average complexity from total metrics."""
        if self._metrics["total_functions"] > 0:
            self._metrics["average_complexity"] = (
                self._metrics["total_complexity"] / self._metrics["total_functions"]
            )
    
    def analyze(self) -> Dict[str, Any]:
        """Analyze code complexity.
        
        Returns:
            Dict[str, Any]: Analysis results
        """
        self._reset_metrics()
        
        # Get Python files to analyze
        files = self._get_python_files()
        
        # Process each file
        for file_path in files:
            if self._should_process_file(file_path):
                metrics = self._process_file(file_path)
                if metrics and not metrics.get("error"):
                    self._metrics["files"].append(metrics)
        
        self._calculate_average_complexity()
        return self._metrics
    
    def _filter_dirs(self, dirs: List[str]) -> List[str]:
        """Filter out ignored directories."""
        if not self.config:
            return [d for d in dirs if not any(pattern in d for pattern in self.IGNORED_PATTERNS)]
            
        patterns = self.config.analysis.exclude_patterns
        return [d for d in dirs if not any(pattern in d for pattern in patterns)]
    
    def _should_analyze_test_file(self, file_path: Path) -> bool:
        """Check if a test file should be analyzed."""
        if not self.config or self.config.analysis.analyze_tests:
            return True
            
        return not any(
            file_path.match(pattern)
            for pattern in self.config.analysis.test_patterns
        )
    
    def _collect_python_file(self, root_path: Path, file: str) -> Optional[Path]:
        """Process a single file and return its path if valid."""
        if not file.endswith('.py'):
            return None
            
        file_path = root_path / file
        if not self._should_analyze_test_file(file_path):
            return None
            
        if self._should_process_file(file_path):
            return file_path
        return None
    
    def _get_python_files(self) -> List[Path]:
        """Get all Python files in the current directory.
        
        Returns:
            List[Path]: List of Python file paths
        """
        python_files = []
        for root, dirs, files in os.walk('.'):
            # Filter directories in-place
            dirs[:] = self._filter_dirs(dirs)
            
            # Process files
            root_path = Path(root)
            for file in files:
                if file_path := self._collect_python_file(root_path, file):
                    python_files.append(file_path)
        
        return python_files
    
    def _process_file(self, file_path: Path) -> Dict[str, Any]:
        """Process a single file.
        
        Args:
            file_path (Path): Path to the file
            
        Returns:
            Dict[str, Any]: File metrics
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            visitor = ComplexityVisitor()
            visitor.visit(tree)
            
            # Calculate metrics based on configuration
            metrics = {
                "file_path": str(file_path),
                "cyclomatic_complexity": visitor.complexity,
                "functions": visitor.functions
            }
            
            # Add optional metrics based on configuration
            if self.config and self.config.metrics.maintainability_index:
                metrics["maintainability_index"] = self.metrics_calculator.calculate_maintainability_index(
                    content, visitor.complexity, len(visitor.functions)
                )
            
            if self.config and self.config.metrics.halstead_metrics:
                metrics["halstead_metrics"] = self.metrics_calculator.calculate_halstead_metrics(content)
            
            # Update global metrics
            self._metrics["total_complexity"] += visitor.complexity
            self._metrics["total_functions"] += len(visitor.functions)
            
            return metrics
            
        except Exception as e:
            return {
                "file_path": str(file_path),
                "error": str(e),
                "cyclomatic_complexity": 1,
                "functions": [],
                "maintainability_index": 0 if self.config and self.config.metrics.maintainability_index else None,
                "halstead_metrics": (
                    {"volume": 0, "difficulty": 0, "effort": 0}
                    if self.config and self.config.metrics.halstead_metrics
                    else None
                )
            } 