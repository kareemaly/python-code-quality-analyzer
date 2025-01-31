import ast
from pathlib import Path
from typing import List

from code_analyzer.models.complexity import ComplexFunction

class ComplexityVisitor(ast.NodeVisitor):
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.complex_functions: List[ComplexFunction] = []
        self.current_function = None
        self.current_complexity = 0

    def visit_FunctionDef(self, node: ast.FunctionDef):
        parent_function = self.current_function
        parent_complexity = self.current_complexity
        
        self.current_function = node.name
        self.current_complexity = 1  # Base complexity
        
        # Visit function body
        self.generic_visit(node)
        
        # Store function complexity
        self.complex_functions.append(ComplexFunction(
            name=node.name,
            complexity=self.current_complexity,
            location=self.file_path
        ))
        
        self.current_function = parent_function
        self.current_complexity = parent_complexity

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self.visit_FunctionDef(node)  # Reuse FunctionDef logic

    def visit_If(self, node: ast.If):
        self.current_complexity += 1  # Each if branch adds complexity
        self.generic_visit(node)

    def visit_While(self, node: ast.While):
        self.current_complexity += 1  # While loop adds complexity
        self.generic_visit(node)

    def visit_For(self, node: ast.For):
        self.current_complexity += 1  # For loop adds complexity
        self.generic_visit(node)

    def visit_AsyncFor(self, node: ast.AsyncFor):
        self.current_complexity += 1  # Async for loop adds complexity
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        self.current_complexity += 1  # Each except handler adds complexity
        self.generic_visit(node)

    def visit_With(self, node: ast.With):
        self.current_complexity += 1  # With block adds complexity
        self.generic_visit(node)

    def visit_AsyncWith(self, node: ast.AsyncWith):
        self.current_complexity += 1  # Async with block adds complexity
        self.generic_visit(node)

    def visit_BoolOp(self, node: ast.BoolOp):
        if isinstance(node.op, ast.And) or isinstance(node.op, ast.Or):
            self.current_complexity += len(node.values) - 1  # Each boolean operator adds complexity
        self.generic_visit(node) 