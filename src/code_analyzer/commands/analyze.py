"""
Analyze command for code analysis
"""

import csv
import json
import os
import sys
import traceback
from fnmatch import fnmatch
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.console import Console

from ..analyzers import ComplexityAnalyzer, DeadCodeAnalyzer, SimilarityAnalyzer
from ..config import ConfigLoader
from ..formatters.console import ConsoleFormatter
from .base_command import BaseCommand


class AnalyzeCommand(BaseCommand):
    """Command to analyze code complexity and quality metrics"""

    def __init__(self, config_path: Optional[str] = None, **options):
        """Initialize the analyze command.
        
        Args:
            config_path: Optional path to configuration file
            **options: Additional options from CLI
        """
        super().__init__()
        self.error_console = Console(file=sys.stderr)
        self.console = Console()
        self.formatter = ConsoleFormatter()
        
        # Initialize default config
        self.config = {
            "analysis": {
                "exclude_patterns": [],
                "min_complexity": 10,
                "dead_code": {"enabled": True},
                "similarity": {"enabled": True}
            },
            "output": {
                "verbose": False,
                "format": "console"
            }
        }
        
        # Load config from file if provided
        if config_path:
            try:
                with open(config_path) as f:
                    file_config = json.load(f)
                    self._merge_config(file_config)
            except Exception as e:
                self._log_error(f"Error loading config from {config_path}: {e}")
        
        # Update config with CLI options
        if options.get("verbose"):
            self.config["output"]["verbose"] = True
        if options.get("output"):
            self.config["output"]["format"] = options["output"]
        if options.get("min_complexity"):
            self.config["analysis"]["min_complexity"] = options["min_complexity"]
        if options.get("exclude"):
            self.config["analysis"]["exclude_patterns"].extend(options["exclude"])
        
        self.complexity_analyzer = ComplexityAnalyzer(self.config)
        self.dead_code_analyzer = DeadCodeAnalyzer(self.config)
        self.similarity_analyzer = SimilarityAnalyzer(self.config)
        self.target_path: Optional[Path] = None
        self.had_errors = False

    def _merge_config(self, new_config: Dict[str, Any]) -> None:
        """Merge new config with existing config.
        
        Args:
            new_config: New configuration to merge
        """
        for section, values in new_config.items():
            if section not in self.config:
                self.config[section] = {}
            if isinstance(values, dict):
                for key, value in values.items():
                    self.config[section][key] = value
            else:
                self.config[section] = values

    def run(self, paths: List[str]) -> int:
        """Run code analysis.
        
        Args:
            paths: List of paths to analyze
            
        Returns:
            int: Exit code
        """
        try:
            self._setup(paths)
            self._validate_setup()
            
            results = {}
            
            with Progress() as progress:
                task = progress.add_task("Analyzing...", total=len(self.python_files))
                
                # Run complexity analysis
                complexity_results = {}
                for file_path in self.python_files:
                    try:
                        file_results = self.complexity_analyzer.analyze(file_path)
                        if file_results:
                            complexity_results["files"] = complexity_results.get("files", []) + [file_results]
                    except Exception as e:
                        self._log_error(f"Error analyzing {file_path}: {str(e)}")
                        if self.config["output"]["verbose"]:
                            self._log_error(traceback.format_exc())
                        self.had_errors = True
                    progress.update(task, advance=1)
                
                if complexity_results:
                    results.update(complexity_results)
                
                # Run dead code analysis if enabled
                if self.config["analysis"]["dead_code"]["enabled"]:
                    try:
                        dead_code_results = self.dead_code_analyzer.analyze(self.python_files)
                        if dead_code_results:
                            results.update(dead_code_results)
                    except Exception as e:
                        self._log_error(f"Error in dead code analysis: {str(e)}")
                        if self.config["output"]["verbose"]:
                            self._log_error(traceback.format_exc())
                            
                # Run similarity analysis if enabled
                if self.config["analysis"]["similarity"]["enabled"]:
                    try:
                        similarity_results = self.similarity_analyzer.analyze(self.python_files)
                        if similarity_results:
                            results.update(similarity_results)
                    except Exception as e:
                        self._log_error(f"Error in similarity analysis: {str(e)}")
                        if self.config["output"]["verbose"]:
                            self._log_error(traceback.format_exc())
                            
            # Format and output results
            if results:
                if self.config["output"]["format"] == "json":
                    print(json.dumps(results, indent=2))
                elif self.config["output"]["format"] == "csv":
                    self._write_csv(results)
                else:
                    self.formatter.format(results)
                    
            return 1 if self.had_errors else 0
                
        except Exception as e:
            self._log_error(str(e))
            if self.config["output"]["verbose"]:
                self._log_error(traceback.format_exc())
            return 1

    def _log_error(self, message: str) -> None:
        """Log an error message.
        
        Args:
            message: Error message to log
        """
        self.error_console.print(f"[red]Error:[/red] {message}")

    def _setup(self, paths: List[str]) -> None:
        """Setup analysis paths.
        
        Args:
            paths: List of paths to analyze
        """
        if not paths:
            paths = ["."]
            
        self.target_path = Path(paths[0]).resolve()
        self.python_files = list(self._find_python_files())

    def _validate_setup(self) -> None:
        """Validate analysis setup."""
        if not self.target_path or not self.target_path.exists():
            raise ValueError(f"Path does not exist: {self.target_path}")
            
        if not self.python_files:
            raise ValueError(f"No Python files found in {self.target_path}")

    def _find_python_files(self) -> Iterator[Path]:
        """Find Python files to analyze.
        
        Returns:
            Iterator[Path]: Iterator of Python file paths
        """
        if self.target_path.is_file():
            if self.target_path.suffix == ".py":
                yield self.target_path
            return

        for root, _, files in os.walk(self.target_path):
            root_path = Path(root)
            
            # Skip excluded directories
            if any(fnmatch(str(root_path), pattern) for pattern in self.config["analysis"]["exclude_patterns"]):
                continue
                
            for file in files:
                if not file.endswith(".py"):
                    continue
                    
                file_path = root_path / file
                if any(fnmatch(str(file_path), pattern) for pattern in self.config["analysis"]["exclude_patterns"]):
                    continue
                    
                yield file_path

    def _write_csv(self, results: Dict[str, Any]) -> None:
        """Write results to CSV.
        
        Args:
            results: Analysis results to write
        """
        if "files" not in results:
            return
            
        writer = csv.DictWriter(sys.stdout, fieldnames=["file", "complexity", "maintainability"])
        writer.writeheader()
        
        for file_result in results["files"]:
            writer.writerow({
                "file": file_result["file_path"],
                "complexity": file_result.get("cyclomatic_complexity", 0),
                "maintainability": file_result.get("maintainability_index", 100)
            })
