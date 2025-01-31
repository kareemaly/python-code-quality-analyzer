"""
Console formatter for rich terminal output
"""

from typing import Any, Dict, List, Optional
from rich.table import Table
from rich.tree import Tree
from rich.panel import Panel
from rich.syntax import Syntax
from rich.columns import Columns

from .base_formatter import BaseFormatter

class ConsoleFormatter(BaseFormatter):
    """Formatter for console output using rich"""
    
    def format(self, data: Dict[str, Any]) -> Any:
        """Format data based on its type and structure"""
        if not data:
            return Panel("No data available", title="Empty Result")
        
        if "error" in data:
            return Panel(f"[red]{data['error']}[/red]", title="Error")
        
        # Create panels for different sections
        panels = []
        
        # Performance metrics
        if "analysis_time" in data:
            panels.append(self._format_performance(data))
        
        # Metrics by file
        if "metrics" in data:
            panels.append(self._format_metrics(data["metrics"]))
        
        # Summary
        if "summary" in data:
            panels.append(self._format_summary(data["summary"]))
        
        return Columns(panels)
    
    def _format_performance(self, data: Dict[str, Any]) -> Panel:
        """Format performance metrics"""
        lines = [
            "[bold]Performance Metrics[/bold]",
            f"Total analysis time: {data['analysis_time']:.2f}s"
        ]
        
        # Add per-file performance if available
        metrics = data.get("metrics", {})
        if metrics:
            total_file_time = sum(
                m.get("performance", {}).get("total_time", 0)
                for m in metrics.values()
            )
            avg_file_time = total_file_time / len(metrics) if metrics else 0
            
            lines.extend([
                f"Average time per file: {avg_file_time:.3f}s",
                "\n[bold]Slowest Files:[/bold]"
            ])
            
            # Show top 5 slowest files
            sorted_files = sorted(
                [(f, m["performance"]["total_time"]) for f, m in metrics.items() if "performance" in m],
                key=lambda x: x[1],
                reverse=True
            )
            
            for file_path, time_taken in sorted_files[:5]:
                lines.append(f"{file_path}: {time_taken:.3f}s")
        
        return Panel("\n".join(lines), title="Performance")
    
    def _format_metrics(self, metrics: Dict[str, Any]) -> Panel:
        """Format file metrics"""
        if not metrics:
            return Panel("No metrics available", title="Metrics")
        
        table = self._create_table(
            "File Metrics",
            ["File", "Complexity", "MI", "LOC", "Functions"]
        )
        
        for file_path, data in metrics.items():
            complexity = data.get("complexity", {})
            maintainability = data.get("maintainability", {})
            size = data.get("size", {})
            
            table.add_row(
                file_path,
                f"{complexity.get('average', 0):.1f}",
                f"{maintainability.get('index', 0):.1f} ({maintainability.get('rank', 'N/A')})",
                str(size.get("loc", 0)),
                str(len(complexity.get("functions", [])))
            )
        
        return Panel(table, title="Metrics by File")
    
    def _format_summary(self, summary: Dict[str, Any]) -> Panel:
        """Format analysis summary"""
        if not summary:
            return Panel("No summary available", title="Summary")
        
        lines = [
            "[bold]Analysis Summary[/bold]",
            f"Total files: {summary.get('total_files', 0)}",
            f"Total functions: {summary.get('total_functions', 0)}",
            f"Average complexity: {summary.get('average_complexity', 0):.2f}",
            f"Average maintainability: {summary.get('average_maintainability', 0):.2f}"
        ]
        
        # Add high complexity functions
        high_complexity = summary.get("high_complexity_functions", [])
        if high_complexity:
            lines.extend([
                "\n[bold red]High Complexity Functions:[/bold red]"
            ])
            
            for func in high_complexity[:5]:
                lines.append(
                    f"{func['file']}::{func['name']} "
                    f"(complexity: {func['complexity']}, line: {func['line_number']})"
                )
        
        return Panel("\n".join(lines), title="Summary")
    
    def _is_tabular_data(self, data: Dict[str, Any]) -> bool:
        """Check if data is suitable for table format"""
        if isinstance(data, dict) and data:
            first_value = next(iter(data.values()))
            return isinstance(first_value, (dict, list)) and all(
                isinstance(v, type(first_value)) for v in data.values()
            )
        return False
    
    def _is_tree_data(self, data: Dict[str, Any]) -> bool:
        """Check if data is suitable for tree format"""
        return isinstance(data, dict) and any(
            isinstance(v, (dict, list)) for v in data.values()
        )
    
    def _is_code_data(self, data: Dict[str, Any]) -> bool:
        """Check if data contains code"""
        return isinstance(data, dict) and any(
            isinstance(v, str) and (v.startswith("def ") or v.startswith("class "))
            for v in data.values()
        )
    
    def _format_table(self, data: Dict[str, Any]) -> Table:
        """Format data as table"""
        if isinstance(next(iter(data.values())), dict):
            # Dictionary of dictionaries
            columns = ["Key"] + list(next(iter(data.values())).keys())
            table = self._create_table("Data Table", columns)
            
            for key, value in data.items():
                row = [key] + [str(v) for v in value.values()]
                table.add_row(*row)
        else:
            # Dictionary of lists or simple values
            columns = list(data.keys())
            table = self._create_table("Data Table", columns)
            
            if isinstance(next(iter(data.values())), list):
                # Transpose lists to rows
                rows = zip(*[data[col] for col in columns])
                for row in rows:
                    table.add_row(*[str(cell) for cell in row])
            else:
                table.add_row(*[str(v) for v in data.values()])
        
        return table
    
    def _format_tree(self, data: Dict[str, Any]) -> Tree:
        """Format data as tree"""
        tree = self._create_tree("Data Tree")
        
        def add_node(parent: Tree, key: str, value: Any) -> None:
            if isinstance(value, dict):
                branch = parent.add(f"[cyan]{key}[/cyan]")
                for k, v in value.items():
                    add_node(branch, k, v)
            elif isinstance(value, list):
                branch = parent.add(f"[cyan]{key}[/cyan]")
                for i, item in enumerate(value):
                    add_node(branch, str(i), item)
            else:
                parent.add(f"[cyan]{key}[/cyan]: {value}")
        
        for key, value in data.items():
            add_node(tree, key, value)
        
        return tree
    
    def _format_code(self, data: Dict[str, Any]) -> Panel:
        """Format code with syntax highlighting"""
        code_blocks = []
        for key, value in data.items():
            if isinstance(value, str) and (value.startswith("def ") or value.startswith("class ")):
                code_blocks.append(f"# {key}")
                code_blocks.append(value)
        
        return Panel(
            Syntax("\n\n".join(code_blocks), "python", theme="monokai"),
            title="Code View"
        )
    
    def _format_panel(self, data: Dict[str, Any]) -> Panel:
        """Format data as simple panel"""
        lines = []
        
        def format_value(value: Any, indent: int = 0) -> str:
            if isinstance(value, (dict, list)):
                return str(value)
            return str(value)
        
        for key, value in data.items():
            lines.append(f"{' ' * 2}{key}: {format_value(value)}")
        
        return Panel("\n".join(lines), title="Data View") 