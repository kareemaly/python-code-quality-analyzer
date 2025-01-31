"""
Analyze command for code analysis
"""

import json
import csv
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List, Iterator
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn, TextColumn
from fnmatch import fnmatch

from ..analyzers.complexity import ComplexityAnalyzer
from ..formatters.console import ConsoleFormatter
from ..config.config_loader import ConfigLoader, Config
from .base_command import BaseCommand

class AnalyzeCommand(BaseCommand):
    """Command to analyze code complexity and quality metrics"""
    
    def __init__(self):
        super().__init__()
        self.formatter = ConsoleFormatter()
        self.config_loader = ConfigLoader()
        self.config: Optional[Config] = None
        self.analyzer: Optional[ComplexityAnalyzer] = None
        self.target_path: Optional[Path] = None
    
    def run(self, target_path: Optional[str] = None, output_format: Optional[str] = None,
            min_complexity: Optional[int] = None, exclude_patterns: Optional[List[str]] = None,
            verbose: Optional[bool] = None, config_path: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Run code analysis
        
        Args:
            target_path: Path to analyze (default: current directory)
            output_format: Output format (console, json, csv)
            min_complexity: Minimum complexity to highlight
            exclude_patterns: Glob patterns to exclude
            verbose: Enable verbose output
            config_path: Path to configuration file
            
        Returns:
            Dict[str, Any]: Analysis results
        """
        try:
            # Load configuration
            cli_options = self._build_cli_options(
                output_format, min_complexity, exclude_patterns, verbose
            )
            self.config = self.config_loader.load_config(config_path, cli_options)
            
            self._initialize_analysis(target_path)
            metrics = self._perform_analysis()
            self._output_results(metrics)
            return metrics
            
        except Exception as e:
            self._handle_error(e)
            return {}
    
    def _build_cli_options(self, output_format: Optional[str], min_complexity: Optional[int],
                          exclude_patterns: Optional[List[str]], verbose: Optional[bool]) -> Dict[str, Any]:
        """Build CLI options dictionary."""
        options: Dict[str, Any] = {}
        
        if output_format:
            options["output"] = {"format": output_format}
        if min_complexity:
            options["analysis"] = {"min_complexity": min_complexity}
        if exclude_patterns:
            if "analysis" not in options:
                options["analysis"] = {}
            options["analysis"]["exclude_patterns"] = exclude_patterns
        if verbose is not None:
            if "output" not in options:
                options["output"] = {}
            options["output"]["verbose"] = verbose
        
        return options

    def _initialize_analysis(self, target_path: Optional[str]) -> None:
        """Initialize analysis configuration and setup."""
        if not self.config:
            raise ValueError("Configuration not loaded")
            
        # Set up paths
        self.target_path = Path(target_path) if target_path else Path.cwd()
        
        self._setup()
        self.analyzer = ComplexityAnalyzer(config=self.config, config_root=self.config_root)
        self._validate_setup()
        
        if self.config.output.verbose:
            self._print_analysis_info(f"Analyzing code in {self.target_path}...")
            self._print_analysis_info(f"Excluding patterns: {self.config.analysis.exclude_patterns}")

    def _collect_python_files(self) -> List[Path]:
        """Collect Python files for analysis."""
        python_files = []
        progress = self._create_progress_bar("Collecting Python files...")
        if progress:
            with progress as p:
                task = p.add_task("Collecting Python files...", total=None)
                for file_path in self.target_path.rglob("*.py"):
                    if self._should_process_file(file_path):
                        python_files.append(file_path)
                p.update(task, completed=True)
        else:
            for file_path in self.target_path.rglob("*.py"):
                if self._should_process_file(file_path):
                    python_files.append(file_path)
        
        if not python_files and self.config and self.config.output.verbose:
            self._print_warning("No Python files found to analyze")
        
        return python_files

    def _create_progress_bar(self, description: str) -> Optional[Progress]:
        """Create a progress bar based on configuration."""
        if not self.config or not self.config.output.show_progress or self.config.output.format == 'json':
            return None
            
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
        )
    
    def _log_processing(self, file_path: Path) -> None:
        """Log file processing if verbose mode is enabled."""
        if self.config and self.config.output.verbose:
            self._print_analysis_info(f"Processing {file_path.relative_to(self.target_path)}")
    
    def _log_error(self, file_path: Path, error: Exception) -> None:
        """Log processing error if verbose mode is enabled."""
        if self.config.output.verbose:
            self._print_warning(f"Failed to process {file_path}: {error}")
    
    def _process_single_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Process a single file and return its metrics."""
        if not self.analyzer:
            return None
            
        self._log_processing(file_path)
        try:
            return self.analyzer._process_file(file_path)
        except Exception as e:
            self._log_error(file_path, e)
            return None
    
    def _get_relative_path(self, file_path: Path) -> Optional[Path]:
        """Get path relative to target path."""
        try:
            return file_path.resolve().relative_to(self.target_path.resolve())
        except ValueError:
            return None
    
    def _should_process_file(self, file_path: Path) -> bool:
        """Check if a file should be processed."""
        if not self.config:
            return False
            
        if self.analyzer:
            return self.analyzer._should_process_file(file_path)
            
        if not (rel_path := self._get_relative_path(file_path)):
            return False
            
        return not any(
            fnmatch(str(rel_path), pattern)
            for pattern in self.config.analysis.exclude_patterns
        )
    
    def _analyze_files(self, python_files: List[Path]) -> Dict[str, Any]:
        """Analyze collected Python files."""
        metrics = {
            "files": [],
            "total_complexity": 0,
            "total_functions": 0,
            "average_complexity": 0
        }
        
        progress = self._create_progress_bar("Analyzing files...")
        if progress:
            with progress as p:
                task = p.add_task("Analyzing files...", total=len(python_files))
                for file_path in python_files:
                    if file_metrics := self._process_single_file(file_path):
                        metrics["files"].append(file_metrics)
                    p.advance(task)
        else:
            for file_path in python_files:
                if file_metrics := self._process_single_file(file_path):
                    metrics["files"].append(file_metrics)
        
        return metrics

    def _perform_analysis(self) -> Dict[str, Any]:
        """Perform the code analysis."""
        python_files = self._collect_python_files()
        if not python_files:
            if self.config and self.config.output.verbose:
                self._print_analysis_info("No Python files found to analyze")
            return {
                "files": [],
                "total_complexity": 0,
                "total_functions": 0,
                "average_complexity": 0
            }
        
        metrics = self._analyze_files(python_files)
        self._filter_results(metrics)
        return metrics

    def _output_console(self, metrics: Dict[str, Any]) -> None:
        """Output results to console."""
        if not metrics.get("files"):
            self.console.print("No files analyzed")
            return
            
        formatted = self.formatter.format(metrics)
        self.console.print(formatted)
        self._print_summary(metrics)
    
    def _output_results(self, metrics: Dict[str, Any]) -> None:
        """Output analysis results based on configuration."""
        if not self.config:
            return
            
        output_handlers = {
            'console': self._output_console,
            'json': self._output_json,
            'csv': self._output_csv
        }
        
        # Disable progress bar for JSON output
        if self.config.output.format == 'json':
            self.config.output.show_progress = False
        
        handler = output_handlers.get(self.config.output.format)
        if handler:
            handler(metrics)
            
        if self.config.output.verbose and self.config.output.format != 'json':
            self._print_success("Analysis complete!")
    
    def _filter_file_functions(self, file_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter functions based on configuration."""
        if not self.config or "functions" not in file_data:
            return []
            
        return [
            f for f in file_data["functions"]
            if f.get("complexity", 0) >= self.config.analysis.min_complexity
        ]

    def _calculate_summary_metrics(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary metrics from filtered files."""
        total_complexity = sum(f.get("cyclomatic_complexity", 0) for f in files)
        total_functions = sum(len(f.get("functions", [])) for f in files)
        return {
            "total_complexity": total_complexity,
            "total_functions": total_functions,
            "average_complexity": total_complexity / total_functions if total_functions > 0 else 0
        }

    def _filter_results(self, data: Dict[str, Any]) -> None:
        """Filter results based on configuration."""
        if not self.config or not data or "files" not in data:
            return
            
        filtered_files = []
        for file_data in data["files"]:
            file_path = Path(file_data["file_path"])
            if not self._should_process_file(file_path):
                continue
            
            file_data["functions"] = self._filter_file_functions(file_data)
            filtered_files.append(file_data)
        
        data["files"] = filtered_files
        data.update(self._calculate_summary_metrics(filtered_files))
    
    def _output_json(self, data: Dict[str, Any]) -> None:
        """Output results in JSON format."""
        # Format and output JSON directly
        json.dump(data, sys.stdout, indent=2)
        sys.stdout.write("\n")
    
    def _output_csv(self, data: Dict[str, Any]) -> None:
        """Output results in CSV format."""
        # Clean up progress bar output
        sys.stdout.write("\033[2K\033[1G")  # Clear line and move cursor to start
        
        writer = csv.DictWriter(sys.stdout, fieldnames=["File", "Function", "Complexity", "Line"])
        writer.writeheader()
        
        for file_data in data.get("files", []):
            file_path = file_data.get("file_path", "")
            for func in file_data.get("functions", []):
                writer.writerow({
                    "File": file_path,
                    "Function": func.get("name", ""),
                    "Complexity": func.get("complexity", 0),
                    "Line": func.get("line_number", 0)
                })
    
    def _format_function_info(self, file_path: str, func_name: str, complexity: int, line: int) -> str:
        """Format function information for summary output."""
        return f"  {file_path}::{func_name} (complexity: {complexity}, line: {line})"
    
    def _get_complex_functions(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get list of functions that exceed minimum complexity."""
        complex_funcs = []
        for file_data in metrics.get("files", []):
            file_path = file_data["file_path"]
            for func in file_data.get("functions", []):
                if func.get("complexity", 0) >= self.config.analysis.min_complexity:
                    complex_funcs.append({
                        "file_path": file_path,
                        "name": func["name"],
                        "complexity": func["complexity"],
                        "line": func.get("line_number", 0)
                    })
        return complex_funcs
    
    def _print_summary(self, metrics: Dict[str, Any]) -> None:
        """Print analysis summary."""
        total_files = len(metrics.get("files", []))
        total_functions = metrics.get("total_functions", 0)
        avg_complexity = metrics.get("average_complexity", 0)
        
        self.console.print("\nAnalysis Summary:")
        self.console.print(f"Total files analyzed: {total_files}")
        self.console.print(f"Total functions: {total_functions}")
        self.console.print(f"Average complexity: {avg_complexity:.2f}")
        
        complex_funcs = self._get_complex_functions(metrics)
        if complex_funcs:
            self.console.print(f"Functions with complexity >= {self.config.analysis.min_complexity}:")
            for func in complex_funcs:
                self.console.print(self._format_function_info(
                    func["file_path"], func["name"], 
                    func["complexity"], func["line"]
                ))

    def _print_analysis_info(self, message: str) -> None:
        """Print analysis information in verbose mode."""
        if self.config and self.config.output.verbose:
            self.console.print(f"[blue]{message}[/blue]") 