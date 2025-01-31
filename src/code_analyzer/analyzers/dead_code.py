"""
Dead code analyzer for detecting unused code elements.
Tracks symbols and their usage across Python files.
"""

import ast
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Union

from .base_analyzer import BaseAnalyzer


class SymbolType(Enum):
    """Types of symbols that can be analyzed for usage."""
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    VARIABLE = "variable"
    IMPORT = "import"


@dataclass
class Symbol:
    """A symbol (class, function, variable, etc.) in the code."""
    name: str
    type: SymbolType
    file_path: str
    line: int
    end_line: Optional[int] = None
    parent: Optional['Symbol'] = None
    is_private: bool = False
    is_test: bool = False
    is_special: bool = False
    is_property: bool = False
    is_override: bool = False
    docstring: Optional[str] = None
    decorators: List[str] = field(default_factory=list)
    used_by: Set['Symbol'] = field(default_factory=set)
    uses: Set['Symbol'] = field(default_factory=set)
    
    def __hash__(self):
        return hash((self.name, self.type, self.file_path, self.line))
    
    def __eq__(self, other):
        if not isinstance(other, Symbol):
            return False
        return (self.name == other.name and
                self.type == other.type and
                self.file_path == other.file_path and
                self.line == other.line)


class SymbolTable:
    """Tracks symbols and their relationships."""
    
    def __init__(self):
        self.symbols: Dict[str, Symbol] = {}
        self.file_symbols: Dict[str, List[Symbol]] = {}
        self.current_class: Optional[Symbol] = None
        self.current_function: Optional[Symbol] = None
        self.scope_stack: List[Symbol] = []
    
    def add_symbol(self, symbol: Symbol):
        """Add a symbol to the table."""
        key = f"{symbol.file_path}:{symbol.line}:{symbol.name}"
        self.symbols[key] = symbol
        
        if symbol.file_path not in self.file_symbols:
            self.file_symbols[symbol.file_path] = []
        self.file_symbols[symbol.file_path].append(symbol)
    
    def get_symbol(self, name: str, file_path: str, line: int) -> Optional[Symbol]:
        """Get a symbol by its identifiers."""
        key = f"{file_path}:{line}:{name}"
        return self.symbols.get(key)
    
    def get_file_symbols(self, file_path: str) -> List[Symbol]:
        """Get all symbols defined in a file."""
        return self.file_symbols.get(file_path, [])


class DefinitionVisitor(ast.NodeVisitor):
    """AST visitor for finding symbol definitions."""
    
    def __init__(self, file_path: str, symbol_table: SymbolTable):
        self.file_path = file_path
        self.symbol_table = symbol_table
        self.current_class = None
        self.current_function = None
        self.imported_names = set()
    
    def visit_ClassDef(self, node):
        """Visit class definition."""
        old_class = self.current_class
        
        # Create class symbol
        symbol = Symbol(
            name=node.name,
            type=SymbolType.CLASS,
            file_path=self.file_path,
            line=node.lineno,
            end_line=node.end_lineno,
            docstring=ast.get_docstring(node),
            decorators=[
                ast.unparse(d).strip()
                for d in node.decorator_list
            ],
            is_private=node.name.startswith('_'),
            is_test=node.name.startswith('Test') or node.name.endswith('Test')
        )
        
        if old_class:
            symbol.parent = old_class
            
        self.symbol_table.add_symbol(symbol)
        self.current_class = symbol
        
        # Visit class body
        self.generic_visit(node)
        
        self.current_class = old_class
    
    def visit_FunctionDef(self, node):
        """Visit function definition."""
        old_function = self.current_function
        
        # Determine if this is a method
        symbol_type = SymbolType.METHOD if self.current_class else SymbolType.FUNCTION
        
        # Create function/method symbol
        symbol = Symbol(
            name=node.name,
            type=symbol_type,
            file_path=self.file_path,
            line=node.lineno,
            end_line=node.end_lineno,
            parent=self.current_class,
            docstring=ast.get_docstring(node),
            decorators=[
                ast.unparse(d).strip()
                for d in node.decorator_list
            ],
            is_private=node.name.startswith('_'),
            is_test=node.name.startswith('test_'),
            is_special=node.name.startswith('__') and node.name.endswith('__'),
            is_property=any(
                d.id == 'property'
                for d in node.decorator_list
                if isinstance(d, ast.Name)
            ),
            is_override=any(
                d.id == 'override'
                for d in node.decorator_list
                if isinstance(d, ast.Name)
            )
        )
        
        self.symbol_table.add_symbol(symbol)
        self.current_function = symbol
        
        # Visit function body
        self.generic_visit(node)
        
        self.current_function = old_function
    
    def visit_AsyncFunctionDef(self, node):
        """Visit async function definition."""
        self.visit_FunctionDef(node)  # Handle same as sync functions
    
    def visit_Import(self, node):
        """Visit import statement."""
        for alias in node.names:
            name = alias.asname or alias.name
            symbol = Symbol(
                name=name,
                type=SymbolType.IMPORT,
                file_path=self.file_path,
                line=node.lineno,
                is_private=name.startswith('_')
            )
            self.symbol_table.add_symbol(symbol)
            self.imported_names.add(name)
    
    def visit_ImportFrom(self, node):
        """Visit from-import statement."""
        for alias in node.names:
            name = alias.asname or alias.name
            if name == '*':
                continue  # Skip wildcard imports
            symbol = Symbol(
                name=name,
                type=SymbolType.IMPORT,
                file_path=self.file_path,
                line=node.lineno,
                is_private=name.startswith('_')
            )
            self.symbol_table.add_symbol(symbol)
            self.imported_names.add(name)


class UsageVisitor(ast.NodeVisitor):
    """AST visitor for finding symbol usage."""
    
    def __init__(self, file_path: str, symbol_table: SymbolTable):
        self.file_path = file_path
        self.symbol_table = symbol_table
        self.current_scope = None
        self.used_names = set()
    
    def visit_Name(self, node):
        """Visit name node."""
        if isinstance(node.ctx, ast.Load):
            self.used_names.add(node.id)
            
            # Try to find the symbol in the current file
            symbol = self.symbol_table.get_symbol(node.id, self.file_path, node.lineno)
            if symbol and self.current_scope:
                symbol.used_by.add(self.current_scope)
                self.current_scope.uses.add(symbol)
    
    def visit_ClassDef(self, node):
        """Visit class definition."""
        old_scope = self.current_scope
        self.current_scope = self.symbol_table.get_symbol(
            node.name,
            self.file_path,
            node.lineno
        )
        
        # Visit bases and decorators
        for base in node.bases:
            self.visit(base)
        for decorator in node.decorator_list:
            self.visit(decorator)
            
        # Visit class body
        self.generic_visit(node)
        
        self.current_scope = old_scope
    
    def visit_FunctionDef(self, node):
        """Visit function definition."""
        old_scope = self.current_scope
        self.current_scope = self.symbol_table.get_symbol(
            node.name,
            self.file_path,
            node.lineno
        )
        
        # Visit decorators
        for decorator in node.decorator_list:
            self.visit(decorator)
            
        # Visit function body
        self.generic_visit(node)
        
        self.current_scope = old_scope
    
    def visit_AsyncFunctionDef(self, node):
        """Visit async function definition."""
        self.visit_FunctionDef(node)  # Handle same as sync functions


class DeadCodeAnalyzer(BaseAnalyzer):
    """Analyzer for finding unused code."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the analyzer.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__(config)
        self.symbol_table = SymbolTable()
        dead_code_config = config.get("analysis", {}).get("dead_code", {})
        self.ignore_private = dead_code_config.get("ignore_private", True)
        self.ignore_special = dead_code_config.get("ignore_special", True)
        self.ignore_overrides = dead_code_config.get("ignore_overrides", True)
        self.ignore_properties = dead_code_config.get("ignore_properties", True)
        self.ignore_test_files = dead_code_config.get("ignore_test_files", True)

    def analyze(self, file_paths: List[Path]) -> Dict[str, Any]:
        """Analyze files for unused code.
        
        Args:
            file_paths: List of paths to analyze
            
        Returns:
            Dict containing dead code analysis results
        """
        # First pass: collect all symbols
        for file_path in file_paths:
            if self.should_ignore_file(file_path):
                continue
                
            try:
                self._collect_symbols(file_path)
            except Exception as e:
                self._log_error(f"Error collecting symbols from {file_path}: {str(e)}")
        
        # Second pass: analyze usage
        for file_path in file_paths:
            if self.should_ignore_file(file_path):
                continue
                
            try:
                self._analyze_usage(file_path)
            except Exception as e:
                self._log_error(f"Error analyzing usage in {file_path}: {str(e)}")
        
        # Find unused symbols
        unused_classes = []
        unused_functions = []
        unused_methods = []
        unused_variables = []
        unused_imports = []
        
        for symbol in self.symbol_table.symbols.values():
            if self._should_ignore_symbol(symbol):
                continue
                
            if not symbol.used_by:
                result = {
                    'name': symbol.name,
                    'file': symbol.file_path,
                    'line': symbol.line,
                    'end_line': symbol.end_line,
                    'type': symbol.type.value
                }
                
                if symbol.type == SymbolType.CLASS:
                    unused_classes.append(result)
                elif symbol.type == SymbolType.FUNCTION:
                    unused_functions.append(result)
                elif symbol.type == SymbolType.METHOD:
                    unused_methods.append(result)
                elif symbol.type == SymbolType.VARIABLE:
                    unused_variables.append(result)
                elif symbol.type == SymbolType.IMPORT:
                    unused_imports.append(result)
        
        return {
            'unused_classes': unused_classes,
            'unused_functions': unused_functions,
            'unused_methods': unused_methods,
            'unused_variables': unused_variables,
            'unused_imports': unused_imports,
            'total_unused': (
                len(unused_classes) +
                len(unused_functions) +
                len(unused_methods) +
                len(unused_variables) +
                len(unused_imports)
            )
        }

    def _collect_symbols(self, file_path: Path):
        """Collect symbols from a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            tree = ast.parse(content)
            visitor = DefinitionVisitor(str(file_path), self.symbol_table)
            visitor.visit(tree)
            
        except Exception as e:
            self._log_error(f"Error parsing {file_path}: {str(e)}")

    def _analyze_usage(self, file_path: Path):
        """Analyze symbol usage in a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            tree = ast.parse(content)
            visitor = UsageVisitor(str(file_path), self.symbol_table)
            visitor.visit(tree)
            
        except Exception as e:
            self._log_error(f"Error analyzing {file_path}: {str(e)}")

    def _should_ignore_symbol(self, symbol: Symbol) -> bool:
        """Check if a symbol should be ignored in dead code analysis."""
        if symbol.is_test and self.ignore_test_files:
            return True
            
        if symbol.is_private and self.ignore_private:
            return True
            
        if symbol.is_special and self.ignore_special:
            return True
            
        if symbol.is_override and self.ignore_overrides:
            return True
            
        if symbol.is_property and self.ignore_properties:
            return True
            
        return False 