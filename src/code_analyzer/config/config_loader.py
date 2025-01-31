"""
Configuration loader for code analyzer
"""

from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional, List

import yaml


class ConfigError(Exception):
    """Exception raised for configuration errors."""
    pass


DEFAULT_CONFIG_PATH = Path(__file__).parent / "default_config.yaml"


@dataclass
class DeadCodeConfig:
    """Dead code analysis configuration."""
    enabled: bool = True
    ignore_private: bool = False
    ignore_test_files: bool = True
    min_references: int = 1
    ignore_patterns: list = field(default_factory=lambda: ["**/tests/**", "setup.py", "conftest.py"])
    ignore_names: list = field(default_factory=lambda: ["__init__", "__main__", "main", "setup"])

    def __post_init__(self):
        if self.ignore_patterns is None:
            self.ignore_patterns = []
        if self.ignore_names is None:
            self.ignore_names = []


@dataclass
class LSHConfig:
    """LSH configuration settings."""
    num_bands: int = 10
    band_size: int = 2


@dataclass
class SimilarityConfig:
    """Similarity analysis configuration."""
    enabled: bool = True
    min_fragment_size: int = 5
    similarity_threshold: float = 0.8
    ignore_test_files: bool = True
    ignore_patterns: list = field(default_factory=lambda: ["**/tests/**", "setup.py", "conftest.py"])
    ignore_names: list = field(default_factory=lambda: ["__init__", "__main__", "main", "setup"])
    lsh_config: LSHConfig = field(default_factory=LSHConfig)

    def __post_init__(self):
        if self.ignore_patterns is None:
            self.ignore_patterns = []
        if self.ignore_names is None:
            self.ignore_names = []
        if self.lsh_config is None:
            self.lsh_config = LSHConfig()


@dataclass
class ComplexityConfig:
    enabled: bool = True
    max_complexity: int = 10
    min_complexity: int = 1
    ignore_patterns: list = field(default_factory=list)
    ignore_private: bool = False
    ignore_names: list = field(default_factory=list)

    def __post_init__(self):
        if self.ignore_patterns is None:
            self.ignore_patterns = []
        if self.ignore_names is None:
            self.ignore_names = []


@dataclass
class AnalysisConfig:
    """Analysis configuration settings."""

    min_complexity: int = 5
    exclude_patterns: list = field(default_factory=list)
    analyze_tests: bool = False
    test_patterns: list = field(default_factory=list)
    dead_code: DeadCodeConfig = field(default_factory=DeadCodeConfig)
    complexity: ComplexityConfig = field(default_factory=ComplexityConfig)
    similarity: SimilarityConfig = field(default_factory=SimilarityConfig)

    def __post_init__(self):
        if self.dead_code is None:
            self.dead_code = DeadCodeConfig()
        if self.complexity is None:
            self.complexity = ComplexityConfig()
        if self.similarity is None:
            self.similarity = SimilarityConfig()


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
    search_paths: Optional[List[Path]] = None

    def __post_init__(self):
        if self.analysis is None:
            self.analysis = AnalysisConfig()
        if self.search_paths is None:
            self.search_paths = [Path(".")]


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
            config = self._load_config_from_file(DEFAULT_CONFIG_PATH)
            if config:
                structured_config = self._convert_to_structured_config(config)
                self._update_config_from_dict(structured_config)
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

    def _get_config_paths(self, config_path: Optional[Path] = None) -> List[Path]:
        """Get list of possible configuration file paths."""
        return [
            p for p in [
                config_path,
                Path.cwd() / "code_analyzer.yaml",
                Path.cwd() / "code_analyzer.yml",
                Path.cwd() / ".code_analyzer.yaml",
                Path.cwd() / ".code_analyzer.yml",
                Path.home() / ".code_analyzer.yml",
            ] if p is not None
        ]

    def _load_config_from_file(self, path: Path) -> Optional[Dict[str, Any]]:
        """Load configuration from a file.
        
        Args:
            path: Path to configuration file
            
        Returns:
            Optional[Dict[str, Any]]: Loaded configuration or None if failed
        """
        try:
            with open(path, "r") as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Warning: Error loading config from {path}: {e}")
            return None

    def _convert_to_structured_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Convert raw config dict to structured format.
        
        Args:
            config: Raw configuration dictionary
            
        Returns:
            Dict[str, Any]: Structured configuration
        """
        structured_config = {}
        for section in ["analysis", "output", "metrics", "reports", "server"]:
            if section in config:
                structured_config[section] = {}
                section_obj = getattr(self._config, section)
                for key, value in config[section].items():
                    if hasattr(section_obj, key):
                        structured_config[section][key] = value
        return structured_config

    def _get_current_config_dict(self) -> Dict[str, Any]:
        """Get current configuration as dictionary.
        
        Returns:
            Dict[str, Any]: Current configuration
        """
        return {
            section: {
                k: getattr(getattr(self._config, section), k)
                for k in dir(getattr(self._config, section))
                if not k.startswith("_")
            }
            for section in ["analysis", "output", "metrics", "reports", "server"]
        }

    def _update_config_from_dict(self, config_dict: Dict[str, Any]) -> None:
        """Update configuration object from dictionary.
        
        Args:
            config_dict: Configuration dictionary to apply
        """
        for section, values in config_dict.items():
            if hasattr(self._config, section):
                section_obj = getattr(self._config, section)
                for key, value in values.items():
                    if hasattr(section_obj, key):
                        setattr(section_obj, key, value)

    def _load_local_config(self, config_path: Optional[Path] = None) -> None:
        """Load configuration from local file."""
        paths = self._get_config_paths(config_path)

        for path in paths:
            if path.exists():
                config = self._load_config_from_file(path)
                if config:
                    structured_config = self._convert_to_structured_config(config)
                    current_config = self._get_current_config_dict()
                    merged = self._merge_configs(current_config, structured_config)
                    self._update_config_from_dict(merged)
                break
            elif path == config_path:  # Only raise error if it's the explicitly provided path
                raise FileNotFoundError(f"Config file not found: {path}")

    def _update_config(self, config_dict: Dict[str, Any]) -> None:
        """Update configuration from dictionary."""
        if not config_dict:
            return

        structured_config = self._convert_to_structured_config(config_dict)
        current_config = self._get_current_config_dict()
        merged = self._merge_configs(current_config, structured_config)
        self._update_config_from_dict(merged)

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

    def _validate_config_value(self, key: str, value: Any, schema: Dict[str, Any]) -> bool:
        """Validate a configuration value against its schema.

        Args:
            key: The configuration key
            value: The value to validate
            schema: The schema to validate against

        Returns:
            True if the value is valid, False otherwise
        """
        if key not in schema:
            return True

        current_schema = schema[key]
        value_type = current_schema.get('type')
        allowed_values = current_schema.get('allowed_values', [])

        if value_type and not isinstance(value, self._get_type(value_type)):
            self._print_warning(f"Invalid type for {key}: expected {value_type}, got {type(value).__name__}")
            return False

        if allowed_values and str(value) not in [str(v) for v in allowed_values]:
            self._print_warning(f"Invalid value for {key}: {value}. Allowed values: {allowed_values}")
            return False

        return True
