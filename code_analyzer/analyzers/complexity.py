"""
Code complexity analyzer
"""

import ast
import fnmatch
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from ..config.config_loader import Config
from ..metrics.complexity import ComplexityMetrics, ComplexityVisitor
from .base_analyzer import BaseAnalyzer


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
        return {"files": [], "total_complexity": 0, "average_complexity": 0, "total_functions": 0}

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
        files = self._collect_python_files()

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

        return not any(file_path.match(pattern) for pattern in self.config.analysis.test_patterns)

    def _should_process_file(self, file_path: Path) -> bool:
        """Check if a file should be processed.

        Args:
            file_path: Path to the file

        Returns:
            bool: Whether the file should be processed
        """
        if not self.config:
            return True

        # Get relative path for pattern matching
        try:
            rel_path = str(file_path.resolve().relative_to(Path.cwd().resolve()))
        except ValueError:
            # If we can't get relative path, use absolute path
            rel_path = str(file_path)

        # Check exclude patterns
        for pattern in self.config.analysis.exclude_patterns:
            if pattern.startswith("**/"):
                # Match against any part of the path
                if fnmatch.fnmatch(rel_path, pattern[3:]):
                    return False
            else:
                # Match against full path
                if fnmatch.fnmatch(rel_path, pattern):
                    return False

        # Check test patterns if not analyzing tests
        if not self.config.analysis.analyze_tests:
            for pattern in self.config.analysis.test_patterns:
                if pattern.startswith("**/"):
                    if fnmatch.fnmatch(rel_path, pattern[3:]):
                        return False
                else:
                    if fnmatch.fnmatch(rel_path, pattern):
                        return False

        return True

    def _collect_python_files(self) -> List[Path]:
        """Collect Python files for analysis."""
        python_files = []
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
        ) as progress:
            task = progress.add_task("Collecting Python files...", total=None)

            # Start from target path if set, otherwise current directory
            start_path = self.target_path if self.target_path else Path.cwd()

            for file_path in start_path.rglob("*.py"):
                if self._should_process_file(file_path):
                    python_files.append(file_path)

            progress.update(task, completed=True)

        if not python_files and self.config.output.verbose:
            self._print_warning("No Python files found to analyze")

        return python_files

    def _process_file(self, file_path: Path) -> Dict[str, Any]:
        """Process a single file.

        Args:
            file_path (Path): Path to the file

        Returns:
            Dict[str, Any]: File metrics
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)
            visitor = ComplexityVisitor()
            visitor.visit(tree)

            # Calculate all metrics
            metrics = {
                "file_path": str(file_path),
                "cyclomatic_complexity": visitor.complexity,
                "functions": visitor.functions,
                "maintainability_index": self.metrics_calculator.calculate_maintainability_index(
                    content, visitor.complexity, len(visitor.functions)
                ),
                "halstead_metrics": self.metrics_calculator.calculate_halstead_metrics(content),
            }

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
                "maintainability_index": 0,
                "halstead_metrics": {"volume": 0, "difficulty": 0, "effort": 0},
            }
