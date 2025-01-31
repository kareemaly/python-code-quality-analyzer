"""Tests for the ConsoleFormatter class."""

import pytest
from rich.console import Console
from rich.table import Table

from code_analyzer.formatters.console import ConsoleFormatter


class TestConsoleFormatter:
    @pytest.fixture
    def formatter(self):
        """Create a ConsoleFormatter instance."""
        return ConsoleFormatter()

    @pytest.fixture
    def sample_metrics(self):
        """Create sample metrics for testing."""
        return {
            "files": [
                {
                    "file_path": "test.py",
                    "cyclomatic_complexity": 5,
                    "functions": [{"name": "test_func", "complexity": 3, "line_number": 10}],
                    "maintainability_index": 75.5,
                    "halstead_metrics": {"volume": 100, "difficulty": 10, "effort": 1000},
                }
            ],
            "total_complexity": 5,
            "average_complexity": 3,
            "total_functions": 1,
        }

    def test_formatter_initialization(self, formatter):
        """Test that formatter initializes correctly."""
        assert isinstance(formatter, ConsoleFormatter)
        assert hasattr(formatter, "format")
        assert hasattr(formatter, "_create_performance_table")
        assert hasattr(formatter, "_create_metrics_table")
        assert hasattr(formatter, "_create_summary_table")

    def test_format_returns_string(self, formatter, sample_metrics):
        """Test that format method returns a string."""
        result = formatter.format(sample_metrics)
        assert isinstance(result, str)
        assert "test.py" in result
        assert "test_func" in result

    def test_performance_table_creation(self, formatter, sample_metrics):
        """Test performance table creation."""
        table = formatter._create_performance_table(sample_metrics)
        assert isinstance(table, Table)
        assert table.title == "Performance"

    def test_metrics_table_creation(self, formatter, sample_metrics):
        """Test metrics table creation."""
        table = formatter._create_metrics_table(sample_metrics)
        assert isinstance(table, Table)
        assert table.title == "Metrics by File"

    def test_summary_table_creation(self, formatter, sample_metrics):
        """Test summary table creation."""
        table = formatter._create_summary_table(sample_metrics)
        assert isinstance(table, Table)
        assert table.title == "Summary"

    def test_maintainability_index_color(self, formatter):
        """Test maintainability index color coding."""
        assert formatter._get_mi_color(90) == "green"
        assert formatter._get_mi_color(70) == "yellow"
        assert formatter._get_mi_color(50) == "red"

    def test_complexity_color(self, formatter):
        """Test complexity color coding."""
        assert formatter._get_complexity_color(1) == "green"
        assert formatter._get_complexity_color(5) == "yellow"
        assert formatter._get_complexity_color(10) == "red"

    def test_format_handles_empty_metrics(self, formatter):
        """Test handling of empty metrics."""
        empty_metrics = {
            "files": [],
            "total_complexity": 0,
            "average_complexity": 0,
            "total_functions": 0,
        }
        result = formatter.format(empty_metrics)
        assert isinstance(result, str)
        assert "No files analyzed" in result

    def test_format_handles_missing_data(self, formatter):
        """Test handling of metrics with missing data."""
        incomplete_metrics = {
            "files": [
                {
                    "file_path": "test.py",
                    "cyclomatic_complexity": 5,
                    # Missing other fields
                }
            ],
            "total_complexity": 5,
            # Missing other fields
        }
        result = formatter.format(incomplete_metrics)
        assert isinstance(result, str)
        assert "test.py" in result

    def test_format_handles_errors(self, formatter):
        """Test handling of metrics with errors."""
        metrics_with_error = {
            "files": [
                {
                    "file_path": "test.py",
                    "error": "Failed to analyze file",
                    "cyclomatic_complexity": 1,
                    "functions": [],
                    "maintainability_index": 0,
                    "halstead_metrics": {"volume": 0, "difficulty": 0, "effort": 0},
                }
            ],
            "total_complexity": 0,
            "average_complexity": 0,
            "total_functions": 0,
        }
        result = formatter.format(metrics_with_error)
        assert isinstance(result, str)
        assert "Failed to analyze file" in result
