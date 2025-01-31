"""Tests for configuration loader"""

from pathlib import Path

import pytest
import yaml

from code_analyzer.config.config_loader import ConfigLoader


@pytest.fixture
def temp_config_file(tmp_path):
    """Create a temporary config file."""
    config = {
        "analysis": {"min_complexity": 10, "exclude_patterns": ["*.test.py"]},
        "output": {"format": "json", "verbose": True},
    }
    config_path = tmp_path / "test_config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config, f)
    return config_path


class TestConfigLoader:
    def test_default_config_loading(self):
        """Test loading default configuration."""
        loader = ConfigLoader()
        assert loader.min_complexity == 5
        assert isinstance(loader.exclude_patterns, list)
        assert loader.output_format == "console"
        assert loader.show_progress is True
        assert loader.verbose is False
        assert loader.use_color is True

    def test_user_config_override(self, temp_config_file):
        """Test user configuration overrides defaults."""
        loader = ConfigLoader(temp_config_file)
        assert loader.min_complexity == 10
        assert loader.exclude_patterns == ["*.test.py"]
        assert loader.output_format == "json"
        assert loader.verbose is True
        # Default values should remain
        assert loader.show_progress is True
        assert loader.use_color is True

    def test_get_value_with_defaults(self):
        """Test getting values with defaults."""
        loader = ConfigLoader()
        assert loader.get_value("nonexistent", default=42) == 42
        assert loader.get_value("analysis", "nonexistent", default="test") == "test"

    def test_complexity_thresholds(self):
        """Test getting complexity thresholds."""
        loader = ConfigLoader()
        thresholds = loader.complexity_thresholds
        assert isinstance(thresholds, dict)
        assert all(k in thresholds for k in ["low", "medium", "high"])
        assert thresholds["low"] < thresholds["medium"] < thresholds["high"]

    def test_maintainability_thresholds(self):
        """Test getting maintainability thresholds."""
        loader = ConfigLoader()
        thresholds = loader.maintainability_thresholds
        assert isinstance(thresholds, dict)
        assert all(k in thresholds for k in ["low", "medium", "high"])
        assert thresholds["low"] < thresholds["medium"] < thresholds["high"]

    def test_invalid_config_path(self):
        """Test handling of invalid config path."""
        with pytest.raises(FileNotFoundError):
            ConfigLoader(Path("/nonexistent/config.yaml"))

    def test_merge_configs(self):
        """Test deep merging of configurations."""
        loader = ConfigLoader()
        base = {"a": {"b": 1, "c": 2}, "d": 3}
        override = {"a": {"b": 10, "e": 20}, "f": 30}
        loader._merge_configs(base, override)
        assert base["a"]["b"] == 10  # Overridden
        assert base["a"]["c"] == 2  # Preserved
        assert base["a"]["e"] == 20  # Added
        assert base["d"] == 3  # Preserved
        assert base["f"] == 30  # Added
