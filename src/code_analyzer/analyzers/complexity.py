"""
Complexity analyzer for code analysis.
Combines cyclomatic complexity, cognitive complexity, and maintainability metrics.
"""

import ast
import math
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_analyzer import BaseAnalyzer


class ComplexityVisitor(ast.NodeVisitor):
    """AST visitor for calculating code complexity metrics."""

    def __init__(self):
        self.cyclomatic_complexity = 0
        self.cognitive_complexity = 0
        self.functions = []
        self.current_function = None
        self.nesting_level = 0
        self.loc = 0

    def visit_FunctionDef(self, node):
        """Visit function definition."""
        old_function = self.current_function
        old_complexity = self.cyclomatic_complexity
        old_cognitive = self.cognitive_complexity
        old_nesting = self.nesting_level
        
        # Create function metrics
        self.current_function = {
            'name': node.name,
            'cyclomatic_complexity': 1,  # Base complexity
            'cognitive_complexity': 0,
            'loc': len(node.body),
            'line': node.lineno,
            'end_line': node.end_lineno or node.lineno
        }
        self.cyclomatic_complexity = 1
        self.cognitive_complexity = 0
        self.nesting_level = 0
        
        # Visit function body
        self.generic_visit(node)
        
        # Update function metrics
        self.current_function['cyclomatic_complexity'] = self.cyclomatic_complexity
        self.current_function['cognitive_complexity'] = self.cognitive_complexity
        self.functions.append(self.current_function)
        
        # Update total LOC
        self.loc += len(node.body)
        
        # Restore state
        self.current_function = old_function
        self.cyclomatic_complexity = old_complexity
        self.cognitive_complexity = old_cognitive
        self.nesting_level = old_nesting

    def visit_If(self, node):
        """Visit if statement."""
        self.cyclomatic_complexity += 1
        self.cognitive_complexity += (1 + self.nesting_level)
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1

    def visit_While(self, node):
        """Visit while loop."""
        self.cyclomatic_complexity += 1
        self.cognitive_complexity += (2 + self.nesting_level)  # Loops are more complex
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1

    def visit_For(self, node):
        """Visit for loop."""
        self.cyclomatic_complexity += 1
        self.cognitive_complexity += (2 + self.nesting_level)  # Loops are more complex
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1

    def visit_Try(self, node):
        """Visit try block."""
        self.cyclomatic_complexity += len(node.handlers) + len(node.finalbody)
        self.cognitive_complexity += 1  # Error handling complexity
        self.generic_visit(node)

    def visit_ExceptHandler(self, node):
        """Visit except handler."""
        self.cyclomatic_complexity += 1
        self.cognitive_complexity += 1
        self.generic_visit(node)

    def visit_BoolOp(self, node):
        """Visit boolean operation."""
        self.cyclomatic_complexity += len(node.values) - 1
        self.cognitive_complexity += (len(node.values) - 1)  # Each boolean operation adds complexity
        self.generic_visit(node)


class ComplexityAnalyzer(BaseAnalyzer):
    """Analyzer for code complexity metrics."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the analyzer.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__(config)
        self.metrics = self._create_empty_metrics()

    def analyze(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a file for complexity metrics.
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            Dict containing complexity metrics
        """
        if self.should_ignore_file(file_path):
            return self._create_empty_metrics()

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return {
                'file_path': str(file_path),
                'error': str(e),
                'cyclomatic_complexity': 0,
                'cognitive_complexity': 0,
                'maintainability_index': 0,
                'functions': [],
                'total_functions': 0
            }

        try:
            tree = ast.parse(content)
            visitor = ComplexityVisitor()
            visitor.visit(tree)

            # Calculate metrics
            total_cyclomatic = sum(f['cyclomatic_complexity'] for f in visitor.functions)
            total_cognitive = sum(f['cognitive_complexity'] for f in visitor.functions)
            total_functions = len(visitor.functions)
            
            avg_cyclomatic = total_cyclomatic / total_functions if total_functions > 0 else 0
            avg_cognitive = total_cognitive / total_functions if total_functions > 0 else 0
            
            mi = self._calculate_maintainability_index(content, total_cyclomatic, visitor.loc)

            return {
                'file_path': str(file_path),
                'cyclomatic_complexity': total_cyclomatic,
                'cognitive_complexity': total_cognitive,
                'maintainability_index': mi,
                'functions': visitor.functions,
                'total_functions': total_functions,
                'average_cyclomatic': avg_cyclomatic,
                'average_cognitive': avg_cognitive,
                'loc': visitor.loc
            }

        except SyntaxError as e:
            return {
                'file_path': str(file_path),
                'error': f'Syntax error at line {e.lineno}: {str(e)}',
                'cyclomatic_complexity': 0,
                'cognitive_complexity': 0,
                'maintainability_index': 0,
                'functions': [],
                'total_functions': 0
            }

    def _create_empty_metrics(self) -> Dict[str, Any]:
        """Create empty metrics dictionary."""
        return {
            'file_path': '',
            'cyclomatic_complexity': 0,
            'cognitive_complexity': 0,
            'maintainability_index': 0,
            'functions': [],
            'total_functions': 0,
            'average_cyclomatic': 0,
            'average_cognitive': 0,
            'loc': 0
        }

    def _calculate_maintainability_index(self, content: str, complexity: int, loc: int) -> float:
        """Calculate maintainability index using the Microsoft formula.
        
        MI = max(0, (171 - 5.2 * ln(HV) - 0.23 * CC - 16.2 * ln(LOC)) * 100 / 171)
        
        Args:
            content: File content
            complexity: Cyclomatic complexity
            loc: Lines of code
            
        Returns:
            float: Maintainability index between 0 and 100
        """
        if loc == 0:
            return 100.0
            
        # Calculate Halstead Volume (simplified)
        h_length = len(content.split())
        h_volume = h_length * (len(set(content.split())))
        
        # Avoid log(0)
        if h_volume == 0:
            h_volume = 1
        if loc == 0:
            loc = 1
            
        # Calculate maintainability index
        mi = 171 - 5.2 * math.log(h_volume) - 0.23 * complexity - 16.2 * math.log(loc)
        mi = max(0, mi) * 100 / 171
        
        return round(mi, 2) 