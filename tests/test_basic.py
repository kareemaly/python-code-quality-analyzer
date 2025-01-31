"""Basic tests for python_code_quality_analyzer."""

import pytest

def test_import():
    """Test that the package can be imported."""
    import python_code_quality_analyzer
    assert python_code_quality_analyzer.__version__
