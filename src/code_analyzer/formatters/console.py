"""
Console formatter for rich terminal output
"""

from typing import Any, Dict, Optional
from pathlib import Path

from rich.columns import Columns
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.layout import Layout
from rich.box import Box

from .base_formatter import BaseFormatter


class ConsoleFormatter(BaseFormatter):
    """Formatter for console output using rich"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the console formatter.

        Args:
            config: Optional configuration dictionary
        """
        super().__init__()
        self.config = config or {}
        self.console = Console(record=True)
        self.project_root = Path.cwd()

    def _get_relative_path(self, file_path: str) -> str:
        """Convert absolute path to relative path from project root.
        
        Args:
            file_path: Absolute file path
            
        Returns:
            str: Relative file path
        """
        try:
            return str(Path(file_path).relative_to(self.project_root))
        except ValueError:
            return file_path

    def format(self, results: Dict[str, Any]) -> None:
        """Format analysis results for console output.
        
        Args:
            results: Analysis results
        """
        # Complexity metrics
        if "files" in results:
            complexity_panel = self._format_complexity_results(results)
            self.console.print(complexity_panel)
            self.console.print()
            
        # Dead code analysis
        if "unused_classes" in results:
            dead_code_panel = self._format_dead_code_results(results)
            self.console.print(dead_code_panel)
            self.console.print()
            
        # Similarity analysis
        if "similar_fragments" in results:
            similarity_panel = self._format_similarity_results(results)
            self.console.print(similarity_panel)
            self.console.print()

    def _format_complexity_results(self, results: Dict[str, Any]) -> Panel:
        """Format complexity analysis results.
        
        Args:
            results: Analysis results to format
            
        Returns:
            Panel: Formatted results
        """
        # Create tables
        performance_table = self._create_performance_table(results)
        complex_table = self._create_complex_functions_table(results)
        metrics_table = self._create_metrics_table(results)
        summary_table = self._create_summary_table(results)
        
        # Create layout
        tables = Columns([
            Panel(performance_table, title="Performance"),
            Panel(complex_table, title="Complex Functions"),
            Panel(metrics_table, title="Metrics by File"),
            Panel(summary_table, title="Summary")
        ])
        
        return Panel(
            tables,
            title="Code Analysis Results",
            border_style="blue"
        )

    def _format_dead_code_results(self, results: Dict[str, Any]) -> Panel:
        """Format dead code analysis results.
        
        Args:
            results: Dead code analysis results
            
        Returns:
            Panel: Formatted results panel
        """
        tables = []
        
        # Unused classes
        if results.get("unused_classes"):
            table = Table(title="Unused Classes")
            table.add_column("Class Name", style="cyan")
            table.add_column("File", style="blue")
            table.add_column("Line", style="magenta")
            
            for cls in results["unused_classes"]:
                table.add_row(
                    cls["name"],
                    str(Path(cls["file"]).relative_to(Path.cwd())),
                    str(cls["line"])
                )
            tables.append(table)
            
        # Unused functions
        if results.get("unused_functions"):
            table = Table(title="Unused Functions")
            table.add_column("Function Name", style="cyan")
            table.add_column("File", style="blue")
            table.add_column("Line", style="magenta")
            
            for func in results["unused_functions"]:
                table.add_row(
                    func["name"],
                    str(Path(func["file"]).relative_to(Path.cwd())),
                    str(func["line"])
                )
            tables.append(table)
            
        # Unused methods
        if results.get("unused_methods"):
            table = Table(title="Unused Methods")
            table.add_column("Method Name", style="cyan")
            table.add_column("File", style="blue")
            table.add_column("Line", style="magenta")
            
            for method in results["unused_methods"]:
                table.add_row(
                    method["name"],
                    str(Path(method["file"]).relative_to(Path.cwd())),
                    str(method["line"])
                )
            tables.append(table)
            
        # Unused variables
        if results.get("unused_variables"):
            table = Table(title="Unused Variables")
            table.add_column("Variable Name", style="cyan")
            table.add_column("File", style="blue")
            table.add_column("Line", style="magenta")
            
            for var in results["unused_variables"]:
                table.add_row(
                    var["name"],
                    var["file"],
                    str(var["line"])
                )
            tables.append(table)
            
        # Unused imports
        if results.get("unused_imports"):
            table = Table(title="Unused Imports")
            table.add_column("Import Name", style="cyan")
            table.add_column("File", style="blue")
            table.add_column("Line", style="magenta")
            
            for imp in results["unused_imports"]:
                table.add_row(
                    imp["name"],
                    str(Path(imp["file"]).relative_to(Path.cwd())),
                    str(imp["line"])
                )
            tables.append(table)
            
        # Summary
        total = results.get("total_unused", 0)
        summary = f"\nTotal unused symbols: {total}"
        
        return Panel(
            Columns(tables),
            title="Dead Code Analysis",
            border_style="red" if total > 0 else "green"
        )

    def _format_similarity_results(self, results: Dict[str, Any]) -> Panel:
        """Format similarity analysis results.
        
        Args:
            results: Similarity analysis results
            
        Returns:
            Panel: Formatted results panel
        """
        if not results.get("similar_fragments"):
            return Panel("No similar code fragments found")
            
        tables = []
        
        # Create summary table
        summary_table = Table(title="Similarity Analysis Summary")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="blue")
        
        total_fragments = len(results["similar_fragments"])
        total_files = len(set(f["file"] for group in results["similar_fragments"] for f in group["fragments"]))
        
        summary_table.add_row("Total Similar Groups", str(total_fragments))
        summary_table.add_row("Files Affected", str(total_files))
        tables.append(summary_table)
        
        # Create detailed fragments table
        fragments_table = Table(title="Similar Code Fragments")
        fragments_table.add_column("Group", style="cyan")
        fragments_table.add_column("File", style="blue")
        fragments_table.add_column("Lines", style="magenta")
        fragments_table.add_column("Similarity", style="green")
        
        for i, group in enumerate(results["similar_fragments"], 1):
            for j, fragment in enumerate(group["fragments"]):
                file_path = str(Path(fragment["file"]).relative_to(self.project_root))
                fragments_table.add_row(
                    f"Group {i}" if j == 0 else "",
                    file_path,
                    f"{fragment['start_line']}-{fragment['end_line']}",
                    f"{group['similarity']:.2%}" if j == 0 else ""
                )
                
        tables.append(fragments_table)
        
        return Panel(
            Columns(tables),
            title="Code Similarity Analysis",
            border_style="blue"
        )

    def _create_performance_table(self, results: Dict[str, Any]) -> Table:
        """Create performance metrics table.
        
        Args:
            results: Analysis results
            
        Returns:
            Table: Performance metrics table
        """
        table = Table(title="Performance Metrics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="blue")
        
        total_files = len(results.get("files", []))
        total_functions = sum(file.get("total_functions", 0) for file in results.get("files", []))
        total_complexity = sum(file.get("cyclomatic_complexity", 0) for file in results.get("files", []))
        avg_complexity = total_complexity / total_functions if total_functions > 0 else 0
        
        table.add_row("Total Files", str(total_files))
        table.add_row("Total Functions", str(total_functions))
        table.add_row("Total Cyclomatic Complexity", str(total_complexity))
        table.add_row("Average Complexity", f"{avg_complexity:.2f}")
        
        return table

    def _create_complex_functions_table(self, results: Dict[str, Any]) -> Table:
        """Create complex functions table.
        
        Args:
            results: Analysis results
            
        Returns:
            Table: Complex functions table
        """
        table = Table(title="Complex Functions")
        table.add_column("File/Function", style="cyan")
        table.add_column("Cyclomatic", style="blue")
        table.add_column("Cognitive", style="magenta")
        table.add_column("Line", style="green")
        
        for file_data in results.get("files", []):
            file_path = str(Path(file_data.get("file_path", "")).relative_to(Path.cwd()))
            for func in file_data.get("functions", []):
                if func.get("cyclomatic_complexity", 0) >= 5 or func.get("cognitive_complexity", 0) >= 5:
                    table.add_row(
                        f"{file_path}::{func['name']}",
                        self._color_complexity(func.get("cyclomatic_complexity", 0)),
                        self._color_complexity(func.get("cognitive_complexity", 0)),
                        str(func.get("line", ""))
                    )
        
        return table

    def _create_metrics_table(self, results: Dict[str, Any]) -> Table:
        """Create metrics by file table.
        
        Args:
            results: Analysis results
            
        Returns:
            Table: Metrics by file table
        """
        table = Table(title="Metrics by File")
        table.add_column("File", style="cyan")
        table.add_column("Cyclomatic", style="blue")
        table.add_column("Cognitive", style="magenta")
        table.add_column("MI", style="green")
        table.add_column("LOC", style="yellow")
        
        for file_data in results.get("files", []):
            file_path = str(Path(file_data.get("file_path", "")).relative_to(Path.cwd()))
            table.add_row(
                file_path,
                self._color_complexity(file_data.get("cyclomatic_complexity", 0)),
                self._color_complexity(file_data.get("cognitive_complexity", 0)),
                self._color_mi(file_data.get("maintainability_index", 0)),
                str(file_data.get("loc", 0))
            )
        
        return table

    def _create_summary_table(self, results: Dict[str, Any]) -> Table:
        """Create summary metrics table.
        
        Args:
            results: Analysis results
            
        Returns:
            Table: Summary metrics table
        """
        table = Table(title="Summary Metrics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="blue")
        
        total_files = len(results.get("files", []))
        total_functions = sum(file.get("total_functions", 0) for file in results.get("files", []))
        total_complexity = sum(file.get("cyclomatic_complexity", 0) for file in results.get("files", []))
        total_cognitive = sum(file.get("cognitive_complexity", 0) for file in results.get("files", []))
        total_loc = sum(file.get("loc", 0) for file in results.get("files", []))
        
        avg_complexity = total_complexity / total_functions if total_functions > 0 else 0
        avg_cognitive = total_cognitive / total_functions if total_functions > 0 else 0
        avg_mi = sum(file.get("maintainability_index", 0) for file in results.get("files", [])) / total_files if total_files > 0 else 0
        
        table.add_row("Average MI", self._color_mi(avg_mi))
        table.add_row("Average Cyclomatic", self._color_complexity(avg_complexity))
        table.add_row("Average Cognitive", self._color_complexity(avg_cognitive))
        table.add_row("Total LOC", str(total_loc))
        
        return table

    def _get_mi_color(self, mi: float) -> str:
        """Get color for maintainability index."""
        if mi >= 80:
            return "green"
        elif mi >= 60:
            return "yellow"
        return "red"

    def _get_complexity_color(self, complexity: float) -> str:
        """Get color for complexity value."""
        if complexity <= 4:
            return "green"
        elif complexity <= 7:
            return "yellow"
        return "red"

    def _color_mi(self, mi: float) -> str:
        """Format maintainability index with color."""
        color = self._get_mi_color(mi)
        return f"[{color}]{mi:.1f}[/{color}]"

    def _color_complexity(self, complexity: float) -> str:
        """Format complexity with color."""
        color = self._get_complexity_color(complexity)
        return f"[{color}]{complexity}[/{color}]"
