from pathlib import Path

import pytest

from code_analyzer.analyzers.base_analyzer import BaseAnalyzer


class TestBaseAnalyzer:
    @pytest.fixture
    def analyzer(self):
        class ConcreteAnalyzer(BaseAnalyzer):
            def analyze(self):
                return {"metric": 42}

            def _process_file(self, file_path):
                return {"file_metric": 10}

        return ConcreteAnalyzer()

    def test_analyzer_initialization(self, analyzer):
        """Test that analyzer initializes correctly."""
        assert isinstance(analyzer, BaseAnalyzer)
        assert hasattr(analyzer, "analyze")
        assert hasattr(analyzer, "_process_file")

    def test_analyze_method_exists(self, analyzer):
        """Test that analyze method exists and returns a dict."""
        result = analyzer.analyze()
        assert isinstance(result, dict)
        assert result["metric"] == 42

    def test_process_file_method_exists(self, analyzer):
        """Test that _process_file method exists and returns a dict."""
        result = analyzer._process_file(Path("dummy.py"))
        assert isinstance(result, dict)
        assert result["file_metric"] == 10

    def test_get_metrics_returns_dict(self, analyzer):
        """Test that get_metrics returns a dictionary."""
        metrics = analyzer.get_metrics()
        assert isinstance(metrics, dict)

    @pytest.mark.parametrize(
        "path,expected",
        [
            ("test.py", True),
            ("test.pyc", False),
            ("test.pyo", False),
            ("__pycache__/test.py", False),
            (".venv/lib/test.py", False),
            ("node_modules/test.py", False),
        ],
    )
    def test_should_process_file(self, analyzer, path, expected):
        """Test file filtering logic."""
        assert analyzer._should_process_file(Path(path)) == expected
