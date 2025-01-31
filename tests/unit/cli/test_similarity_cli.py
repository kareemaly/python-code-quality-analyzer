"""Unit tests for the similarity analyzer CLI."""

import json
import os
import pytest
from src.cli.similarity_cli import collect_python_files, format_results
from src.analyzers.similarity_analyzer import (
    FragmentType,
    Location,
    CodeFragment
)

@pytest.fixture
def temp_python_files(tmp_path):
    """Create temporary Python files for testing."""
    # Create test files
    file1 = tmp_path / "test1.py"
    file2 = tmp_path / "test2.py"
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    file3 = subdir / "test3.py"
    
    file1.write_text("def test1(): pass")
    file2.write_text("def test2(): pass")
    file3.write_text("def test3(): pass")
    
    return tmp_path

def test_collect_python_files(temp_python_files):
    """Test Python file collection."""
    # Test single file
    files = collect_python_files([str(temp_python_files / "test1.py")])
    assert len(files) == 1
    assert files[0].endswith("test1.py")
    
    # Test directory
    files = collect_python_files([str(temp_python_files)])
    assert len(files) == 3
    assert all(f.endswith(".py") for f in files)
    
    # Test mixed paths
    files = collect_python_files([
        str(temp_python_files / "test1.py"),
        str(temp_python_files / "subdir")
    ])
    assert len(files) == 2
    
    # Test non-existent path
    files = collect_python_files([str(temp_python_files / "nonexistent")])
    assert len(files) == 0

def test_format_results():
    """Test results formatting for JSON output."""
    # Create test fragments and results
    fragment1 = CodeFragment(
        type=FragmentType.FUNCTION,
        location=Location("test1.py", 1, 5),
        source="def test1():\n    pass"
    )
    
    fragment2 = CodeFragment(
        type=FragmentType.FUNCTION,
        location=Location("test2.py", 1, 5),
        source="def test2():\n    pass"
    )
    
    results = {
        "test1.py:1": [(fragment2, 0.9)],
        "test2.py:1": [(fragment1, 0.9)]
    }
    
    # Format results
    formatted = format_results(results)
    
    # Verify structure
    assert isinstance(formatted, dict)
    assert len(formatted) == 2
    assert "test1.py:1" in formatted
    assert "test2.py:1" in formatted
    
    # Verify content
    for fragments in formatted.values():
        assert isinstance(fragments, list)
        assert len(fragments) == 1
        fragment = fragments[0]
        assert isinstance(fragment, dict)
        assert all(key in fragment for key in [
            'file', 'start_line', 'end_line', 'type', 'similarity', 'source'
        ])
        assert fragment['similarity'] == 0.9
        assert fragment['type'] == FragmentType.FUNCTION.value

def test_format_results_empty():
    """Test formatting empty results."""
    formatted = format_results({})
    assert isinstance(formatted, dict)
    assert len(formatted) == 0 