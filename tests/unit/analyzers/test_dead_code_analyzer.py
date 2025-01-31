"""
Tests for dead code analyzer
"""

import ast
from pathlib import Path
from textwrap import dedent
from typing import Dict, Any
import shutil

import pytest

from code_analyzer.analyzers.dead_code import (
    DeadCodeAnalyzer,
    Symbol,
    SymbolType,
    Location,
    Reference,
    SymbolGraph,
    SymbolDefVisitor,
    SymbolRefVisitor,
)
from code_analyzer.config.config_loader import Config, DeadCodeConfig


@pytest.fixture
def test_dir():
    """Fixture to create and cleanup test directory."""
    tmp_path = Path("test_files")
    if tmp_path.exists():
        shutil.rmtree(tmp_path)
    tmp_path.mkdir()
    yield tmp_path
    if tmp_path.exists():
        shutil.rmtree(tmp_path)


@pytest.fixture
def test_config():
    """Fixture for test configuration."""
    config = Config()
    config.analysis.dead_code = DeadCodeConfig()
    return config


@pytest.fixture
def analyzer(test_config, test_dir):
    """Fixture for dead code analyzer."""
    return DeadCodeAnalyzer(config=test_config, search_paths=[test_dir])


def test_symbol_graph_add_symbol():
    """Test adding symbols to graph."""
    graph = SymbolGraph()
    symbol = Symbol(
        name="test_func",
        type=SymbolType.FUNCTION,
        location=Location(file="test.py", line=1, column=0)
    )
    
    graph.add_symbol(symbol)
    assert "test_func" in graph.symbols
    assert graph.symbols["test_func"] == symbol


def test_symbol_graph_add_reference():
    """Test adding references to graph."""
    graph = SymbolGraph()
    ref = Reference(
        name="test_func",
        location=Location(file="test.py", line=10, column=4)
    )
    
    graph.add_reference(ref)
    assert "test_func" in graph.references
    assert ref in graph.references["test_func"]


def test_symbol_graph_get_unused_symbols():
    """Test getting unused symbols from graph."""
    graph = SymbolGraph()
    
    # Add used symbol
    used = Symbol(
        name="used_func",
        type=SymbolType.FUNCTION,
        location=Location(file="test.py", line=1, column=0)
    )
    graph.add_symbol(used)
    graph.add_reference(Reference(
        name="used_func",
        location=Location(file="test.py", line=10, column=4)
    ))
    
    # Add unused symbol
    unused = Symbol(
        name="unused_func",
        type=SymbolType.FUNCTION,
        location=Location(file="test.py", line=5, column=0)
    )
    graph.add_symbol(unused)
    
    # Add special method (should be ignored)
    special = Symbol(
        name="__str__",
        type=SymbolType.METHOD,
        location=Location(file="test.py", line=15, column=4)
    )
    graph.add_symbol(special)
    
    unused_symbols = graph.get_unused_symbols()
    assert len(unused_symbols) == 1
    assert unused_symbols[0] == unused


def test_symbol_def_visitor():
    """Test symbol definition visitor."""
    code = dedent("""
        class TestClass:
            def test_method(self):
                pass
                
        def test_function():
            x = 1
            
        CONSTANT = 42
        
        from module import thing
        import other_thing
        
        __all__ = ['TestClass']
    """)
    
    visitor = SymbolDefVisitor("test.py")
    visitor.visit(ast.parse(code))
    
    # Verify symbols found
    symbol_types = {s.name: s.type for s in visitor.symbols}
    expected_types = {
        'TestClass': SymbolType.CLASS,
        'test_method': SymbolType.METHOD,
        'test_function': SymbolType.FUNCTION,
        'x': SymbolType.VARIABLE,
        'CONSTANT': SymbolType.VARIABLE,
        'thing': SymbolType.IMPORT,
        'other_thing': SymbolType.IMPORT,
    }
    assert symbol_types == expected_types
    
    # Verify exports found
    assert visitor.exports == {'TestClass'}


def test_symbol_ref_visitor():
    """Test symbol reference visitor."""
    code = dedent("""
        def test_function():
            helper_function()
            x = SomeClass()
            x.some_method()
            return CONSTANT
    """)
    
    graph = SymbolGraph()
    visitor = SymbolRefVisitor(graph, "test.py")
    visitor.visit(ast.parse(code))
    
    # Verify references found
    ref_names = {r.name for r in graph.references.get('helper_function', [])}
    assert 'helper_function' in ref_names
    
    ref_names = {r.name for r in graph.references.get('SomeClass', [])}
    assert 'SomeClass' in ref_names
    
    ref_names = {r.name for r in graph.references.get('CONSTANT', [])}
    assert 'CONSTANT' in ref_names


def test_dead_code_analyzer_full(test_dir, analyzer):
    """Test full dead code analysis."""
    # File with unused code
    test_file = test_dir / "test.py"
    test_file.write_text(dedent("""
        class UnusedClass:
            def unused_method(self):
                pass
                
        def used_function():
            return 42
            
        def unused_function():
            pass
            
        UNUSED_CONSTANT = 100
        
        from module import unused_import
        import used_import
        
        result = used_function()
        value = used_import.something()
    """))
    
    # Run analysis
    results = analyzer.analyze()
    
    # Verify results
    assert results["total_unused"] > 0
    
    unused_classes = {c["name"] for c in results["unused_classes"]}
    assert "UnusedClass" in unused_classes
    
    unused_methods = {m["name"] for m in results["unused_methods"]}
    assert "unused_method" in unused_methods
    
    unused_functions = {f["name"] for f in results["unused_functions"]}
    assert "unused_function" in unused_functions
    assert "used_function" not in unused_functions
    
    unused_variables = {v["name"] for v in results["unused_variables"]}
    assert "UNUSED_CONSTANT" in unused_variables
    
    unused_imports = {i["name"] for i in results["unused_imports"]}
    assert "unused_import" in unused_imports
    assert "used_import" not in unused_imports


def test_dead_code_analyzer_ignore_patterns(test_dir):
    """Test dead code analyzer with ignore patterns."""
    config = Config()
    config.analysis.dead_code = DeadCodeConfig()
    config.analysis.dead_code.ignore_patterns = ["**/ignored/**"]
    
    analyzer = DeadCodeAnalyzer(config=config, search_paths=[test_dir])
    
    # Create ignored directory
    ignored_dir = test_dir / "ignored"
    ignored_dir.mkdir(exist_ok=True)
    
    # File in ignored directory
    ignored_file = ignored_dir / "ignored.py"
    ignored_file.write_text(dedent("""
        def unused_function():
            pass
    """))
    
    # Normal file
    normal_file = test_dir / "normal.py"
    normal_file.write_text(dedent("""
        def unused_function():
            pass
    """))
    
    # Run analysis
    results = analyzer.analyze()
    
    # Verify only non-ignored files are analyzed
    unused_functions = {
        (f["name"], f["file"]) for f in results["unused_functions"]
    }
    
    assert any(
        f[0] == "unused_function" and "normal.py" in f[1]
        for f in unused_functions
    )
    assert not any(
        f[0] == "unused_function" and "ignored.py" in f[1]
        for f in unused_functions
    )


def test_dead_code_analyzer_ignore_private(test_dir):
    """Test dead code analyzer with ignore_private option."""
    config = Config()
    config.analysis.dead_code = DeadCodeConfig()
    config.analysis.dead_code.ignore_private = True
    
    analyzer = DeadCodeAnalyzer(config=config, search_paths=[test_dir])
    
    # Test file
    test_file = test_dir / "test.py"
    test_file.write_text(dedent("""
        def public_unused():
            pass
            
        def _private_unused():
            pass
    """))
    
    # Run analysis
    results = analyzer.analyze()
    
    # Verify only public unused functions are reported
    unused_functions = {f["name"] for f in results["unused_functions"]}
    assert "public_unused" in unused_functions
    assert "_private_unused" not in unused_functions


def test_dead_code_analyzer_ignore_names(test_dir):
    """Test dead code analyzer with ignore_names option."""
    config = Config()
    config.analysis.dead_code = DeadCodeConfig()
    config.analysis.dead_code.ignore_names = ["ignored_*"]
    
    analyzer = DeadCodeAnalyzer(config=config, search_paths=[test_dir])
    
    # Test file
    test_file = test_dir / "test.py"
    test_file.write_text(dedent("""
        def normal_unused():
            pass
            
        def ignored_unused():
            pass
    """))
    
    # Run analysis
    results = analyzer.analyze()
    
    # Verify only non-ignored unused functions are reported
    unused_functions = {f["name"] for f in results["unused_functions"]}
    assert "normal_unused" in unused_functions
    assert "ignored_unused" not in unused_functions 