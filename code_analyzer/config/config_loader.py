"""
Configuration loader for code analyzer
"""

import os
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

DEFAULT_CONFIG_PATH = Path(__file__).parent / "default_config.yaml"


@dataclass
class AnalysisConfig:
    """Analysis configuration settings."""

    min_complexity: int = 5
    exclude_patterns: list = field(default_factory=list)
    analyze_tests: bool = False
    test_patterns: list = field(default_factory=list)


@dataclass
class OutputConfig:
    """Output configuration settings."""

    format: str = "console"
    verbose: bool = False
    show_progress: bool = True
    show_warnings: bool = True
    colors: Dict[str, Any] = field(
        default_factory=lambda: {
            "enabled": True,
            "error": "red",
            "warning": "yellow",
            "success": "green",
            "info": "blue",
        }
    )


@dataclass
class MetricsConfig:
    """Metrics configuration settings."""

    maintainability_index: bool = True
    halstead_metrics: bool = True
    mi_thresholds: Dict[str, int] = field(
        default_factory=lambda: {"good": 80, "medium": 60, "poor": 40}
    )


@dataclass
class ReportsConfig:
    """Reports configuration settings."""

    output_dir: str = "reports"
    generate_html: bool = True
    track_trends: bool = True
    max_reports: int = 10


@dataclass
class ServerConfig:
    """Server configuration settings."""

    host: str = "localhost"
    port: int = 8000
    auth_enabled: bool = False
    credentials: Dict[str, str] = field(
        default_factory=lambda: {"username": "admin", "password": "admin"}
    )


@dataclass
class Config:
    """Main configuration class."""

    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    metrics: MetricsConfig = field(default_factory=MetricsConfig)
    reports: ReportsConfig = field(default_factory=ReportsConfig)
    server: ServerConfig = field(default_factory=ServerConfig)


class ConfigLoader:
    """Configuration loader for code analyzer."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the configuration loader.

        Args:
            config_path: Optional path to configuration file
        """
        self._config = Config()
        self._load_default_config()
        if config_path:
            self._load_local_config(config_path)

    def _load_default_config(self) -> None:
        """Load default configuration from file."""
        try:
            with open(DEFAULT_CONFIG_PATH, "r") as f:
                default_config = yaml.safe_load(f)
            if default_config:
                # Convert to structured format
                structured_config = {}
                for section in ["analysis", "output", "metrics", "reports", "server"]:
                    if section in default_config:
                        structured_config[section] = {}
                        section_obj = getattr(self._config, section)
                        for key, value in default_config[section].items():
                            if hasattr(section_obj, key):
                                structured_config[section][key] = value

                # Update config with structured values
                for section, values in structured_config.items():
                    if hasattr(self._config, section):
                        section_obj = getattr(self._config, section)
                        for key, value in values.items():
                            if hasattr(section_obj, key):
                                setattr(section_obj, key, value)
        except Exception as e:
            print(f"Warning: Could not load default config: {e}")

    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two configuration dictionaries.

        Args:
            base: Base configuration dictionary
            override: Override configuration dictionary

        Returns:
            Dict[str, Any]: Merged configuration
        """
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_configs(base[key], value)
            else:
                base[key] = value
        return base

    def _load_local_config(self, config_path: Optional[Path] = None) -> None:
        """Load configuration from local file."""
        paths = [
            config_path,
            Path.cwd() / "code_analyzer.yaml",
            Path.cwd() / "code_analyzer.yml",
            Path.cwd() / ".code_analyzer.yaml",
            Path.cwd() / ".code_analyzer.yml",
            Path.home() / ".code_analyzer.yml",
        ]

        for path in filter(None, paths):
            if path.exists():
                try:
                    with open(path, "r") as f:
                        config = yaml.safe_load(f)
                    if config:
                        # Convert to structured format
                        structured_config = {}
                        for section in ["analysis", "output", "metrics", "reports", "server"]:
                            if section in config:
                                structured_config[section] = {}
                                section_obj = getattr(self._config, section)
                                for key, value in config[section].items():
                                    if hasattr(section_obj, key):
                                        structured_config[section][key] = value

                        # Get current config as dict
                        current_config = {
                            "analysis": {
                                k: getattr(self._config.analysis, k)
                                for k in dir(self._config.analysis)
                                if not k.startswith("_")
                            },
                            "output": {
                                k: getattr(self._config.output, k)
                                for k in dir(self._config.output)
                                if not k.startswith("_")
                            },
                            "metrics": {
                                k: getattr(self._config.metrics, k)
                                for k in dir(self._config.metrics)
                                if not k.startswith("_")
                            },
                            "reports": {
                                k: getattr(self._config.reports, k)
                                for k in dir(self._config.reports)
                                if not k.startswith("_")
                            },
                            "server": {
                                k: getattr(self._config.server, k)
                                for k in dir(self._config.server)
                                if not k.startswith("_")
                            },
                        }

                        # Merge configs
                        merged = self._merge_configs(current_config, structured_config)

                        # Update config object with merged values
                        for section, values in merged.items():
                            if hasattr(self._config, section):
                                section_obj = getattr(self._config, section)
                                for key, value in values.items():
                                    if hasattr(section_obj, key):
                                        setattr(section_obj, key, value)
                    break
                except Exception as e:
                    print(f"Warning: Error loading config from {path}: {e}")
            elif path == config_path:  # Only raise error if it's the explicitly provided path
                raise FileNotFoundError(f"Config file not found: {path}")

    def _update_config(self, config_dict: Dict[str, Any]) -> None:
        """Update configuration from dictionary."""
        if not config_dict:
            return

        structured_config = {}

        # Convert config dict to proper structure
        for section in ["analysis", "output", "metrics", "reports", "server"]:
            if section in config_dict:
                structured_config[section] = {}
                for key, value in config_dict[section].items():
                    if hasattr(getattr(self._config, section), key):
                        structured_config[section][key] = value

        # Get current config as dict
        current_config = {
            "analysis": {
                k: getattr(self._config.analysis, k)
                for k in dir(self._config.analysis)
                if not k.startswith("_")
            },
            "output": {
                k: getattr(self._config.output, k)
                for k in dir(self._config.output)
                if not k.startswith("_")
            },
            "metrics": {
                k: getattr(self._config.metrics, k)
                for k in dir(self._config.metrics)
                if not k.startswith("_")
            },
            "reports": {
                k: getattr(self._config.reports, k)
                for k in dir(self._config.reports)
                if not k.startswith("_")
            },
            "server": {
                k: getattr(self._config.server, k)
                for k in dir(self._config.server)
                if not k.startswith("_")
            },
        }

        # Merge configs
        merged = self._merge_configs(current_config, structured_config)

        # Update config object with merged values
        for section, values in merged.items():
            if hasattr(self._config, section):
                section_obj = getattr(self._config, section)
                for key, value in values.items():
                    if hasattr(section_obj, key):
                        setattr(section_obj, key, value)

    def load_config(
        self, config_path: Optional[str] = None, cli_options: Optional[Dict[str, Any]] = None
    ) -> Config:
        """Load configuration from all sources.

        Args:
            config_path: Optional path to configuration file
            cli_options: Optional command line options

        Returns:
            Config: Configuration object
        """
        # Load local config if available
        if config_path:
            self._load_local_config(Path(config_path))
        else:
            self._load_local_config()

        # Override with CLI options
        if cli_options:
            self._update_config(cli_options)

        return deepcopy(self._config)

    @property
    def config(self) -> Config:
        """Get current configuration."""
        return deepcopy(self._config)

    def get_value(self, *keys: str, default: Any = None) -> Any:
        """Get a configuration value by key path.

        Args:
            *keys: Key path to the desired value
            default: Default value if not found

        Returns:
            The configuration value or default
        """
        current = self._config
        for key in keys:
            if not isinstance(current, dict) or key not in current:
                return default
            current = current[key]
        return current

    @property
    def min_complexity(self) -> int:
        """Get minimum complexity threshold."""
        return self._config.analysis.min_complexity

    @property
    def exclude_patterns(self) -> list:
        """Get exclude patterns."""
        return self._config.analysis.exclude_patterns

    @property
    def output_format(self) -> str:
        """Get output format."""
        return self._config.output.format

    @property
    def show_progress(self) -> bool:
        """Get progress bar setting."""
        return self._config.output.show_progress

    @property
    def verbose(self) -> bool:
        """Get verbose output setting."""
        return self._config.output.verbose

    @property
    def use_color(self) -> bool:
        """Get color output setting."""
        return self.get_value("output", "color", default=True)

    @property
    def complexity_thresholds(self) -> Dict[str, int]:
        """Get complexity threshold values."""
        return {
            "low": self.get_value("thresholds", "complexity", "low", default=4),
            "medium": self.get_value("thresholds", "complexity", "medium", default=7),
            "high": self.get_value("thresholds", "complexity", "high", default=10),
        }

    @property
    def maintainability_thresholds(self) -> Dict[str, int]:
        """Get maintainability index threshold values."""
        return {
            "low": self.get_value("thresholds", "maintainability_index", "low", default=40),
            "medium": self.get_value("thresholds", "maintainability_index", "medium", default=60),
            "high": self.get_value("thresholds", "maintainability_index", "high", default=80),
        }
