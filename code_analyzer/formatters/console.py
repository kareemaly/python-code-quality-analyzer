"""
Console formatter for rich terminal output
"""

from typing import Any, Dict

from rich.columns import Columns
from rich.console import Console
from rich.table import Table

from .base_formatter import BaseFormatter


class ConsoleFormatter(BaseFormatter):
    """Formatter for console output using rich"""

    def __init__(self):
        """Initialize the formatter."""
        self.console = Console(record=True)

    def format(self, data: Dict[str, Any]) -> str:
        """Format analysis results for console output.

        Args:
            data: Analysis results to format

        Returns:
            str: Formatted string representation
        """
        if not data or not data.get("files"):
            return "No files analyzed"

        # Print title
        self.console.print("\n[bold cyan]Code Analysis Results[/bold cyan]\n")

        tables = []

        # Create performance table first
        performance_table = self._create_performance_table(data)
        tables.append(performance_table)

        # Create complex functions table
        complex_table = self._create_complex_functions_table(data)
        tables.append(complex_table)

        # Create metrics table
        metrics_table = self._create_metrics_table(data)
        tables.append(metrics_table)

        # Create summary table
        summary_table = self._create_summary_table(data)
        tables.append(summary_table)

        # Render tables in columns
        self.console.print(Columns(tables))

        # Print complex functions summary
        self._print_complex_functions_summary(data)

        return self.console.export_text()

    def _create_performance_table(self, data: Dict[str, Any]) -> Table:
        """Create performance metrics table."""
        table = Table(title="Performance")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", justify="right")

        # Ensure Total Files is always first
        table.add_row("Total Files", str(len(data["files"])))
        table.add_row("Total Functions", str(data.get("total_functions", 0)))
        table.add_row("Average Complexity", f"{data.get('average_complexity', 0):.2f}")

        return table

    def _create_complex_functions_table(self, data: Dict[str, Any]) -> Table:
        """Create complex functions table."""
        table = Table(title="Complex Functions")
        table.add_column("File/Function", style="cyan")
        table.add_column("Complexity")
        table.add_column("Line", justify="right")

        for file_data in data["files"]:
            for func in file_data.get("functions", []):
                if func["complexity"] >= 3:  # Show functions with complexity >= 3
                    table.add_row(
                        f"{file_data['file_path']}::{func['name']}",
                        self._color_complexity(func["complexity"]),
                        str(func.get("line_number", "")),
                    )

        return table

    def _create_metrics_table(self, data: Dict[str, Any]) -> Table:
        """Create detailed metrics table."""
        table = Table(title="Metrics by File")
        table.add_column("File/Function", style="cyan")
        table.add_column("Complexity")
        table.add_column("MI", justify="right")
        table.add_column("Line", justify="right")
        table.add_column("Status", style="red")

        for file_data in data["files"]:
            # Add file row
            file_complexity = file_data.get("cyclomatic_complexity", 0)
            file_mi = file_data.get("maintainability_index", 0)
            error = file_data.get("error", "")

            table.add_row(
                file_data["file_path"],
                self._color_complexity(file_complexity),
                self._color_mi(file_mi),
                "",
                error,
            )

            # Add function rows
            for func in file_data.get("functions", []):
                table.add_row(
                    f"  └─ {func['name']}",
                    self._color_complexity(func["complexity"]),
                    "",
                    str(func.get("line_number", "")),
                    "",
                )

        return table

    def _create_summary_table(self, data: Dict[str, Any]) -> Table:
        """Create summary table."""
        table = Table(title="Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value")

        total_mi = sum(f.get("maintainability_index", 0) for f in data["files"])
        avg_mi = total_mi / len(data["files"]) if data["files"] else 0

        table.add_row("Average MI", f"{avg_mi:.2f}")
        table.add_row("Total Complexity", str(data.get("total_complexity", 0)))
        table.add_row("Average Complexity", f"{data.get('average_complexity', 0):.2f}")

        return table

    def _print_complex_functions_summary(self, data: Dict[str, Any]) -> None:
        """Print summary of complex functions."""
        complex_functions = []
        for file_data in data["files"]:
            for func in file_data.get("functions", []):
                if func["complexity"] >= 3:  # Show functions with complexity >= 3
                    complex_functions.append(
                        {
                            "file": file_data["file_path"],
                            "name": func["name"],
                            "complexity": func["complexity"],
                            "line": func.get("line_number", ""),
                        }
                    )

        if complex_functions:
            self.console.print("\n\nAnalysis Summary:")
            self.console.print(f"Total files analyzed: {len(data['files'])}")
            self.console.print(f"Total functions: {data.get('total_functions', 0)}")
            self.console.print(f"Average complexity: {data.get('average_complexity', 0):.2f}")
            self.console.print("Functions with complexity >= 3:")
            for func in complex_functions:
                self.console.print(
                    f"  {func['file']}::{func['name']} (complexity: {func['complexity']}, line: {func['line']})"
                )

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
