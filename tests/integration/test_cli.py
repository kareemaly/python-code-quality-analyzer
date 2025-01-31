"""Integration tests for the code analyzer CLI."""

import csv
import json
import os
from pathlib import Path

import pytest
from click.testing import CliRunner

from code_analyzer.__main__ import cli


@pytest.fixture
def sample_py_files(tmp_path):
    """Create sample Python files for testing."""
    # Create a simple file
    simple_file = tmp_path / "simple.py"
    simple_file.write_text(
        """
def simple_function():
    return True
"""
    )

    # Create a complex file
    complex_file = tmp_path / "complex.py"
    complex_file.write_text(
        """
def complex_function(x):
    if x > 0:
        for i in range(x):
            if i % 2 == 0:
                print(i)
            else:
                print(i + 1)
    else:
        while x < 0:
            x += 1
            try:
                print(1/x)
            except:
                pass
    return x
"""
    )

    return tmp_path


@pytest.fixture
def config_file(tmp_path):
    """Create a test configuration file."""
    config = {
        "analysis": {"min_complexity": 3, "exclude_patterns": ["**/test_*.py"]},
        "output": {"format": "console", "show_progress": True, "verbose": True},
    }
    config_path = tmp_path / "test_config.yaml"
    import yaml

    with open(config_path, "w") as f:
        yaml.dump(config, f)
    return config_path


class TestCLI:
    def test_analyze_help(self):
        """Test the help output of analyze command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--help"])
        assert result.exit_code == 0
        assert "Analyze code complexity" in result.output

    def test_analyze_simple_directory(self, sample_py_files):
        """Test analyzing a directory with simple Python files."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", str(sample_py_files), "--verbose"])
        assert result.exit_code == 0
        assert "Code Analysis Results" in result.output
        assert "Total Files" in result.output
        assert "Total Functions" in result.output
        assert "Average Complexity" in result.output
        assert "Processing simple.py" in result.output
        assert "Processing complex.py" in result.output

    def test_analyze_with_config(self, sample_py_files, config_file):
        """Test analyzing with a configuration file."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", str(sample_py_files), "--config", str(config_file)])
        assert result.exit_code == 0
        assert "Code Analysis Results" in result.output
        assert "Total Files" in result.output
        assert "Total Functions" in result.output
        assert "Average Complexity" in result.output

    def test_analyze_json_output(self, sample_py_files):
        """Test JSON output format."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", str(sample_py_files), "--format", "json"])
        assert result.exit_code == 0
        # Parse JSON output
        data = json.loads(result.output)
        assert "files" in data
        assert "total_complexity" in data
        assert "total_functions" in data
        assert "average_complexity" in data

    def test_analyze_min_complexity(self, sample_py_files):
        """Test minimum complexity filtering."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", str(sample_py_files), "--min-complexity", "3"])
        assert result.exit_code == 0
        assert "Code Analysis Results" in result.output
        assert "Complex Functions" in result.output

    def test_analyze_exclude_pattern(self, sample_py_files):
        """Test exclude pattern functionality."""
        # Create a test file that should be excluded
        test_file = sample_py_files / "test_exclude.py"
        test_file.write_text("def test(): pass")

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", str(sample_py_files), "--exclude", "**/test_*.py"])
        assert result.exit_code == 0
        assert "test_exclude.py" not in result.output

    def test_analyze_no_progress(self, sample_py_files):
        """Test analysis without progress bar."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", str(sample_py_files), "--no-progress"])
        assert result.exit_code == 0
        # Progress bar characters should not be in output
        assert "%" not in result.output

    def test_analyze_verbose(self, sample_py_files):
        """Test verbose output."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", str(sample_py_files), "--verbose"])
        assert result.exit_code == 0
        assert "Code Analysis Results" in result.output
        assert "Processing" in result.output
