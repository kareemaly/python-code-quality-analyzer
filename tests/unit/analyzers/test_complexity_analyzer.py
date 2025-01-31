"""Tests for the ComplexityAnalyzer class."""

from pathlib import Path
from textwrap import dedent

import pytest

from code_analyzer.analyzers.complexity import ComplexityAnalyzer


class TestComplexityAnalyzer:
    @pytest.fixture
    def analyzer(self):
        """Create a ComplexityAnalyzer instance."""
        return ComplexityAnalyzer()

    @pytest.fixture
    def sample_python_file(self, tmp_path):
        """Create a sample Python file for testing."""
        file_path = tmp_path / "test.py"
        content = dedent(
            """
            def simple_function():
                return 42
            
            def complex_function(x):
                if x > 0:
                    if x < 10:
                        return "small positive"
                    else:
                        return "large positive"
                else:
                    return "negative"
            
            class TestClass:
                def method_a(self):
                    pass
                
                def method_b(self, x):
                    while x > 0:
                        x -= 1
                        if x % 2 == 0:
                            continue
                        print(x)
        """
        )
        file_path.write_text(content)
        return file_path

    def test_analyzer_initialization(self, analyzer):
        """Test that analyzer initializes correctly."""
        assert isinstance(analyzer, ComplexityAnalyzer)

    def test_analyze_empty_file(self, tmp_path):
        """Test analyzing an empty file."""
        file_path = tmp_path / "empty.py"
        file_path.write_text("")
        analyzer = ComplexityAnalyzer()
        metrics = analyzer._process_file(file_path)

        assert metrics["cyclomatic_complexity"] == 1
        assert metrics["maintainability_index"] > 0
        assert "functions" in metrics
        assert len(metrics["functions"]) == 0

    def test_analyze_simple_function(self, tmp_path):
        """Test analyzing a simple function."""
        file_path = tmp_path / "simple.py"
        file_path.write_text(
            dedent(
                """
            def simple_function():
                return 42
        """
            )
        )
        analyzer = ComplexityAnalyzer()
        metrics = analyzer._process_file(file_path)

        assert metrics["cyclomatic_complexity"] == 1
        assert metrics["maintainability_index"] > 0
        assert len(metrics["functions"]) == 1
        assert metrics["functions"][0]["name"] == "simple_function"
        assert metrics["functions"][0]["complexity"] == 1

    def test_analyze_complex_function(self, sample_python_file):
        """Test analyzing a complex function with control flow."""
        analyzer = ComplexityAnalyzer()
        metrics = analyzer._process_file(sample_python_file)

        # Find the complex_function metrics
        complex_func = next(f for f in metrics["functions"] if f["name"] == "complex_function")
        assert complex_func["complexity"] > 1  # Should have higher complexity due to if/else

    def test_analyze_class_methods(self, sample_python_file):
        """Test analyzing class methods."""
        analyzer = ComplexityAnalyzer()
        metrics = analyzer._process_file(sample_python_file)

        # Check both methods are analyzed
        method_names = [f["name"] for f in metrics["functions"]]
        assert "TestClass.method_a" in method_names
        assert "TestClass.method_b" in method_names

        # method_b should have higher complexity due to while and if
        method_b = next(f for f in metrics["functions"] if f["name"] == "TestClass.method_b")
        assert method_b["complexity"] > 1

    def test_maintainability_index_calculation(self, sample_python_file):
        """Test maintainability index calculation."""
        analyzer = ComplexityAnalyzer()
        metrics = analyzer._process_file(sample_python_file)

        assert "maintainability_index" in metrics
        assert 0 <= metrics["maintainability_index"] <= 100

    def test_halstead_metrics_calculation(self, sample_python_file):
        """Test Halstead metrics calculation."""
        analyzer = ComplexityAnalyzer()
        metrics = analyzer._process_file(sample_python_file)

        assert "halstead_metrics" in metrics
        halstead = metrics["halstead_metrics"]
        assert "volume" in halstead
        assert "difficulty" in halstead
        assert "effort" in halstead

    @pytest.mark.parametrize(
        "code,expected_complexity",
        [
            ("def f(): pass", 1),
            ("def f(x): return x > 0", 1),
            ("def f(x):\n if x > 0: return 1\n else: return 0", 2),
            ("def f(x):\n for i in x: pass", 2),
            ("def f(x):\n while x > 0: x -= 1", 2),
            ("def f(x):\n try: x()\n except: pass", 2),
        ],
    )
    def test_cyclomatic_complexity_cases(self, tmp_path, code, expected_complexity):
        """Test cyclomatic complexity calculation for different cases."""
        file_path = tmp_path / "test.py"
        file_path.write_text(dedent(code))
        analyzer = ComplexityAnalyzer()
        metrics = analyzer._process_file(file_path)

        assert metrics["functions"][0]["complexity"] == expected_complexity
