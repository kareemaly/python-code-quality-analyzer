#!/usr/bin/env python3
"""
Script to benchmark code analyzer performance on large codebases.
"""

import sys
import time
from pathlib import Path
import statistics
from typing import Dict, Any, List, Tuple
import git
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.console import Console
from rich.table import Table

from code_analyzer.analyzers.dead_code_analyzer import DeadCodeAnalyzer
from code_analyzer.analyzers.complexity_analyzer import ComplexityAnalyzer
from code_analyzer.config.config_loader import Config, DeadCodeConfig, ComplexityConfig, AnalysisConfig


# Popular Python projects to benchmark against
BENCHMARK_PROJECTS = [
    {
        "name": "requests",
        "url": "https://github.com/psf/requests.git",
        "branch": "main"
    },
    {
        "name": "flask",
        "url": "https://github.com/pallets/flask.git",
        "branch": "main"
    },
    {
        "name": "django",
        "url": "https://github.com/django/django.git",
        "branch": "main"
    }
]


def clone_project(project: Dict[str, str], target_dir: Path) -> Path:
    """Clone a project for benchmarking.
    
    Args:
        project: Project information
        target_dir: Directory to clone into
        
    Returns:
        Path: Path to cloned project
    """
    project_dir = target_dir / project["name"]
    if not project_dir.exists():
        print(f"\nCloning {project['name']} from {project['url']}...")
        git.Repo.clone_from(project["url"], project_dir, branch=project["branch"])
    return project_dir


def count_python_files(path: Path) -> Tuple[int, int]:
    """Count Python files and total lines.
    
    Args:
        path: Path to analyze
        
    Returns:
        Tuple[int, int]: Number of files and total lines
    """
    file_count = 0
    total_lines = 0
    
    for file_path in path.rglob("*.py"):
        if not any(part.startswith(".") or part in {"venv", "__pycache__"} 
                  for part in file_path.parts):
            file_count += 1
            try:
                with open(file_path) as f:
                    total_lines += sum(1 for _ in f)
            except Exception:
                pass
                
    return file_count, total_lines


def benchmark_project(project_dir: Path, iterations: int = 3) -> Dict[str, Any]:
    """Run benchmarks on a project.
    
    Args:
        project_dir: Path to project
        iterations: Number of iterations to run
        
    Returns:
        Dict[str, Any]: Benchmark results
    """
    config = Config()
    config.search_paths = [project_dir]
    config.analysis = AnalysisConfig()
    
    # Configure analyzers
    config.analysis.dead_code = DeadCodeConfig()
    config.analysis.complexity = ComplexityConfig()
    
    dead_code_times = []
    complexity_times = []
    dead_code_results = None
    complexity_results = None
    
    print(f"\nBenchmarking {project_dir.name}...")
    for i in range(iterations):
        print(f"  Run {i + 1}/{iterations}")
        
        # Benchmark dead code analysis
        start_time = time.time()
        dead_code_analyzer = DeadCodeAnalyzer(config)
        dead_code_results = dead_code_analyzer.analyze()
        dead_code_times.append(time.time() - start_time)
        
        # Benchmark complexity analysis
        start_time = time.time()
        complexity_analyzer = ComplexityAnalyzer(config)
        complexity_results = complexity_analyzer.analyze()
        complexity_times.append(time.time() - start_time)
    
    # Count files and lines
    file_count, total_lines = count_python_files(project_dir)
    
    return {
        "name": project_dir.name,
        "files": file_count,
        "lines": total_lines,
        "dead_code": {
            "min_time": min(dead_code_times),
            "max_time": max(dead_code_times),
            "avg_time": statistics.mean(dead_code_times),
            "unused_symbols": len(dead_code_results) if dead_code_results else 0
        },
        "complexity": {
            "min_time": min(complexity_times),
            "max_time": max(complexity_times),
            "avg_time": statistics.mean(complexity_times),
            "complex_functions": len(complexity_results) if complexity_results else 0
        }
    }


def format_time(seconds: float) -> str:
    """Format time in seconds to human readable string."""
    if seconds < 0.001:
        return f"{seconds * 1000000:.1f}µs"
    elif seconds < 1:
        return f"{seconds * 1000:.1f}ms"
    else:
        return f"{seconds:.2f}s"


def print_results(results: List[Dict[str, Any]]) -> None:
    """Print benchmark results in a table."""
    console = Console()
    
    table = Table(title="Code Analyzer Benchmark Results")
    table.add_column("Project", justify="left", style="cyan")
    table.add_column("Files", justify="right")
    table.add_column("Lines", justify="right")
    table.add_column("Dead Code Time", justify="right")
    table.add_column("Unused Symbols", justify="right")
    table.add_column("Complexity Time", justify="right")
    table.add_column("Complex Functions", justify="right")
    
    for result in results:
        table.add_row(
            result["name"],
            str(result["files"]),
            str(result["lines"]),
            format_time(result["dead_code"]["avg_time"]),
            str(result["dead_code"]["unused_symbols"]),
            format_time(result["complexity"]["avg_time"]),
            str(result["complexity"]["complex_functions"])
        )
    
    console.print(table)


def main():
    """Main entry point."""
    # Create benchmark directory
    benchmark_dir = Path("benchmark_projects")
    benchmark_dir.mkdir(exist_ok=True)
    
    results = []
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task("Running benchmarks...", total=len(BENCHMARK_PROJECTS))
        
        for project in BENCHMARK_PROJECTS:
            try:
                project_dir = clone_project(project, benchmark_dir)
                results.append(benchmark_project(project_dir))
                progress.advance(task)
            except Exception as e:
                print(f"Error benchmarking {project['name']}: {e}")
    
    print_results(results)


if __name__ == "__main__":
    main() 