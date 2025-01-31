"""
Code complexity analyzer
"""

import ast
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
import radon.complexity as radon_cc
from radon.metrics import h_visit, mi_visit
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn

from .base_analyzer import BaseAnalyzer

class ComplexityAnalyzer(BaseAnalyzer):
    """Analyzer for code complexity metrics"""
    
    # Paths to ignore during analysis
    IGNORED_DIRS = {
        '.venv', 'venv', 'env',  # Virtual environments
        'node_modules',          # Node.js modules
        '__pycache__',          # Python cache
        '.git',                 # Git directory
        'build', 'dist',        # Build directories
        'site-packages',        # Python packages
        '.pytest_cache',        # Pytest cache
        '.mypy_cache',          # MyPy cache
        '.tox'                  # Tox directory
    }
    
    def __init__(self, target_path: Path, config_root: Optional[Path] = None):
        super().__init__(config_root)
        self.target_path = Path(target_path)
        self.console = Console()
        
    def analyze(self) -> Dict[str, Any]:
        """Analyze code complexity metrics"""
        try:
            start_time = time.time()
            self._validate_paths()
            
            if not self.target_path.exists():
                return self._create_result({}, f"Target path not found: {self.target_path}")
            
            self.console.print("[blue]Starting analysis...[/blue]")
            metrics = self._analyze_directory(self.target_path)
            
            self.console.print("[blue]Creating summary...[/blue]")
            summary = self._create_summary(metrics)
            
            result = {
                "metrics": metrics,
                "summary": summary,
                "target_path": str(self.target_path),
                "analysis_time": time.time() - start_time
            }
            
            return self._create_result(result)
            
        except Exception as e:
            return self._create_result({}, str(e))
    
    def _should_analyze_path(self, path: Path) -> bool:
        """Check if a path should be analyzed"""
        parts = path.parts
        return not any(ignored in parts for ignored in self.IGNORED_DIRS)
    
    def _analyze_directory(self, directory: Path) -> Dict[str, Any]:
        """Analyze all Python files in directory recursively"""
        metrics = {}
        
        # Get list of Python files first, excluding ignored directories
        py_files = [
            f for f in directory.rglob("*.py")
            if self._should_analyze_path(f)
        ]
        total_files = len(py_files)
        
        self.console.print(f"[blue]Found {total_files} Python files to analyze (excluding ignored directories)[/blue]")
        
        with Progress(
            SpinnerColumn(),
            *Progress.get_default_columns(),
            TimeElapsedColumn(),
            console=self.console
        ) as progress:
            task = progress.add_task("Analyzing files...", total=total_files)
            
            for file_path in py_files:
                try:
                    rel_path = str(file_path.relative_to(self.target_path))
                    progress.update(task, description=f"Analyzing {rel_path}")
                    
                    file_metrics = self._analyze_file(file_path)
                    if file_metrics:
                        metrics[rel_path] = file_metrics
                        
                except Exception as e:
                    self.console.print(f"[yellow]Warning: Error analyzing {file_path}: {e}[/yellow]")
                finally:
                    progress.advance(task)
                
        return metrics
    
    def _analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a single Python file"""
        start_time = time.time()
        
        with open(file_path) as f:
            content = f.read()
            
        # Skip empty files
        if not content.strip():
            return {}
            
        try:
            # Parse AST to validate syntax
            ast.parse(content)
        except SyntaxError:
            return {}
            
        # Measure individual metric timings
        timings = {}
        
        # Cyclomatic complexity
        cc_start = time.time()
        cc_results = list(radon_cc.cc_visit(content))
        timings['complexity'] = time.time() - cc_start
        
        # Halstead metrics
        try:
            h_start = time.time()
            h_results = h_visit(content)
            halstead_metrics = {
                "vocabulary": h_results.vocabulary,
                "length": h_results.length,
                "volume": h_results.volume,
                "difficulty": h_results.difficulty,
                "effort": h_results.effort,
                "time": h_results.time,
                "bugs": h_results.bugs
            }
            timings['halstead'] = time.time() - h_start
        except Exception:
            halstead_metrics = {}
            timings['halstead'] = 0
        
        # Maintainability index
        try:
            mi_start = time.time()
            mi_result = mi_visit(content, multi=True)
            timings['maintainability'] = time.time() - mi_start
        except Exception:
            mi_result = 0
            timings['maintainability'] = 0
        
        # Basic metrics
        loc = len(content.splitlines())
        blank_lines = len([line for line in content.splitlines() if not line.strip()])
        
        metrics = {
            "complexity": {
                "total": sum(result.complexity for result in cc_results),
                "average": sum(result.complexity for result in cc_results) / len(cc_results) if cc_results else 0,
                "functions": [
                    {
                        "name": result.name,
                        "complexity": result.complexity,
                        "line_number": result.lineno,
                        "class_name": result.classname if hasattr(result, 'classname') else None
                    }
                    for result in cc_results
                ]
            },
            "halstead": halstead_metrics,
            "maintainability": {
                "index": mi_result,
                "rank": self._get_maintainability_rank(mi_result)
            },
            "size": {
                "loc": loc,
                "blank_lines": blank_lines,
                "code_lines": loc - blank_lines
            },
            "performance": {
                "total_time": time.time() - start_time,
                "timings": timings
            }
        }
        
        return metrics
    
    def _create_summary(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Create summary of analysis results"""
        if not metrics:
            return {}
            
        total_complexity = 0
        total_mi = 0
        total_files = 0
        total_functions = 0
        high_complexity_functions = []
        
        for file_path, file_metrics in metrics.items():
            if not file_metrics:
                continue
                
            total_files += 1
            complexity = file_metrics.get("complexity", {})
            total_complexity += complexity.get("total", 0)
            total_mi += file_metrics.get("maintainability", {}).get("index", 0)
            
            functions = complexity.get("functions", [])
            total_functions += len(functions)
            
            # Track functions with high complexity
            high_complexity = [
                {"file": file_path, **func}
                for func in functions
                if func["complexity"] > 10
            ]
            high_complexity_functions.extend(high_complexity)
        
        return {
            "total_files": total_files,
            "total_functions": total_functions,
            "average_complexity": total_complexity / total_functions if total_functions else 0,
            "average_maintainability": total_mi / total_files if total_files else 0,
            "high_complexity_functions": sorted(
                high_complexity_functions,
                key=lambda x: x["complexity"],
                reverse=True
            )
        }
    
    def _get_maintainability_rank(self, mi_score: float) -> str:
        """Get maintainability rank based on score"""
        if mi_score >= 100:
            return "A"
        elif mi_score >= 80:
            return "B"
        elif mi_score >= 60:
            return "C"
        elif mi_score >= 40:
            return "D"
        else:
            return "F" 