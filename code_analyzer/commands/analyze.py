"""
Analyze command for code analysis
"""

from pathlib import Path
from typing import Optional

from ..analyzers.complexity import ComplexityAnalyzer
from ..formatters.console import ConsoleFormatter
from .base_command import BaseCommand

class AnalyzeCommand(BaseCommand):
    """Command to analyze code complexity and quality metrics"""
    
    def __init__(self):
        super().__init__()
        self.formatter = ConsoleFormatter()
    
    def run(self, target_path: Optional[str] = None, **kwargs) -> None:
        """Run code analysis"""
        try:
            # Set up analyzer
            if target_path:
                path = Path(target_path)
            else:
                path = Path.cwd()
                
            self._setup()
            self.analyzer = ComplexityAnalyzer(path, self.config_root)
            self._validate_setup()
            
            # Run analysis
            self._print_info(f"Analyzing code in {path}...")
            result = self.analyzer.analyze()
            
            if result.error:
                self._handle_error(Exception(result.error))
                return
                
            # Format and display results
            formatted = self.formatter.format(result.data)
            self.console.print(formatted)
            
            # Print summary
            summary = result.data.get("summary", {})
            if summary:
                self._print_summary(summary)
                
            self._print_success("Analysis complete!")
            
        except Exception as e:
            self._handle_error(e)
    
    def _print_summary(self, summary: dict) -> None:
        """Print analysis summary"""
        self.console.print("\n[bold]Analysis Summary:[/bold]")
        self.console.print(f"Total files analyzed: {summary['total_files']}")
        self.console.print(f"Total functions: {summary['total_functions']}")
        self.console.print(f"Average complexity: {summary['average_complexity']:.2f}")
        self.console.print(f"Average maintainability: {summary['average_maintainability']:.2f}")
        
        high_complexity = summary.get("high_complexity_functions", [])
        if high_complexity:
            self.console.print("\n[bold red]High Complexity Functions:[/bold red]")
            for func in high_complexity[:5]:  # Show top 5
                self.console.print(
                    f"  {func['file']}::{func['name']} "
                    f"(complexity: {func['complexity']}, line: {func['line_number']})"
                ) 