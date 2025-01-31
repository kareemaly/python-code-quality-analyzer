"""Tests for the main CLI module."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from code_analyzer.__main__ import analyze, cli


class TestMain:
    def test_cli_version(self):
        """Test CLI version command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "version" in result.output.lower()

    def test_cli_help(self):
        """Test CLI help command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Usage:" in result.output
        assert "analyze" in result.output

    def test_analyze_help(self):
        """Test analyze command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--help"])
        assert result.exit_code == 0
        assert "Analyze code complexity" in result.output
        assert "--format" in result.output
        assert "--min-complexity" in result.output
        assert "--exclude" in result.output
        assert "--no-progress" in result.output
        assert "--verbose" in result.output
        assert "--config" in result.output

    def test_analyze_invalid_path(self):
        """Test analyze command with invalid path."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "/nonexistent/path"])
        assert result.exit_code == 2  # Click returns 2 for invalid arguments
        assert "Error" in result.output

    def test_analyze_invalid_format(self):
        """Test analyze command with invalid format."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", ".", "--format", "invalid"])
        assert result.exit_code == 2
        assert "Invalid value" in result.output

    def test_analyze_invalid_min_complexity(self):
        """Test analyze command with invalid min complexity."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", ".", "--min-complexity", "invalid"])
        assert result.exit_code == 2
        assert "Invalid value" in result.output

    def test_analyze_invalid_config(self):
        """Test analyze command with invalid config file."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", ".", "--config", "/nonexistent/config.yaml"])
        assert result.exit_code == 2  # Click returns 2 for invalid arguments
        assert "Error" in result.output

    def test_analyze_current_directory(self, tmp_path):
        """Test analyze command with current directory."""
        runner = CliRunner()
        with runner.isolated_filesystem() as fs:
            # Create a simple Python file in the isolated filesystem
            test_file = Path(fs) / "test.py"
            test_file.write_text(
                """
def test_function():
    x = 1
    if x > 0:
        return True
    return False
"""
            )

            result = runner.invoke(cli, ["analyze", "--verbose"])
            assert result.exit_code == 0
            assert "Processing test.py" in result.output

    def test_analyze_with_exclude(self, tmp_path):
        """Test analyze command with exclude pattern."""
        runner = CliRunner()
        with runner.isolated_filesystem() as fs:
            # Create test files in the isolated filesystem
            (Path(fs) / "test.py").write_text("def test(): pass")
            (Path(fs) / "test_exclude.py").write_text("def test(): pass")

            result = runner.invoke(cli, ["analyze", "--exclude", "**/test_*.py", "--verbose"])
            assert result.exit_code == 0
            assert "Processing test.py" in result.output
            assert "test_exclude.py" not in result.output

    def test_analyze_verbose_output(self, tmp_path):
        """Test analyze command with verbose output."""
        runner = CliRunner()
        with runner.isolated_filesystem() as fs:
            # Create a test file in the isolated filesystem
            test_file = Path(fs) / "test.py"
            test_file.write_text("def test(): pass")

            result = runner.invoke(cli, ["analyze", "--verbose"])
            assert result.exit_code == 0
            assert "Processing test.py" in result.output

    def test_analyze_no_progress(self, tmp_path):
        """Test analyze command without progress bar."""
        runner = CliRunner()
        with runner.isolated_filesystem() as fs:
            # Create a test file in the isolated filesystem
            test_file = Path(fs) / "test.py"
            test_file.write_text("def test(): pass")

            result = runner.invoke(cli, ["analyze", "--no-progress"])
            assert result.exit_code == 0
            assert "%" not in result.output
