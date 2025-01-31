"""
Configuration loader for code analyzer
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import yaml
from dataclasses import dataclass, field
from copy import deepcopy

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
    colors: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "error": "red",
        "warning": "yellow",
        "success": "green",
        "info": "blue"
    })

@dataclass
class MetricsConfig:
    """Metrics configuration settings."""
    maintainability_index: bool = True
    halstead_metrics: bool = True
    mi_thresholds: Dict[str, int] = field(default_factory=lambda: {
        "good": 80,
        "medium": 60,
        "poor": 40
    })

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
    credentials: Dict[str, str] = field(default_factory=lambda: {
        "username": "admin",
        "password": "admin"
    })

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
    
    def __init__(self):
        """Initialize the configuration loader."""
        self._config = Config()
        self._load_default_config()
    
    def _load_default_config(self) -> None:
        """Load default configuration from file."""
        try:
            with open(DEFAULT_CONFIG_PATH, 'r') as f:
                default_config = yaml.safe_load(f)
            self._update_config(default_config)
        except Exception as e:
            print(f"Warning: Could not load default config: {e}")
    
    def _load_local_config(self, config_path: Optional[Path] = None) -> None:
        """Load configuration from local file."""
        paths = [
            config_path,
            Path.cwd() / "code_analyzer.yaml",
            Path.cwd() / "code_analyzer.yml",
            Path.cwd() / ".code_analyzer.yaml",
            Path.cwd() / ".code_analyzer.yml",
            Path.home() / ".code_analyzer.yaml",
            Path.home() / ".code_analyzer.yml"
        ]
        
        for path in filter(None, paths):
            if path.exists():
                try:
                    with open(path, 'r') as f:
                        config = yaml.safe_load(f)
                    self._update_config(config)
                    break
                except Exception as e:
                    print(f"Warning: Error loading config from {path}: {e}")
    
    def _update_config(self, config_dict: Dict[str, Any]) -> None:
        """Update configuration from dictionary."""
        if not config_dict:
            return
            
        # Update analysis config
        if 'analysis' in config_dict:
            for key, value in config_dict['analysis'].items():
                setattr(self._config.analysis, key, value)
        
        # Update output config
        if 'output' in config_dict:
            for key, value in config_dict['output'].items():
                setattr(self._config.output, key, value)
        
        # Update metrics config
        if 'metrics' in config_dict:
            for key, value in config_dict['metrics'].items():
                setattr(self._config.metrics, key, value)
        
        # Update reports config
        if 'reports' in config_dict:
            for key, value in config_dict['reports'].items():
                setattr(self._config.reports, key, value)
        
        # Update server config
        if 'server' in config_dict:
            for key, value in config_dict['server'].items():
                setattr(self._config.server, key, value)
    
    def load_config(self, config_path: Optional[str] = None,
                   cli_options: Optional[Dict[str, Any]] = None) -> Config:
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
        return self.get_value("analysis", "min_complexity", default=5)
    
    @property
    def exclude_patterns(self) -> list:
        """Get exclude patterns."""
        return self.get_value("analysis", "exclude_patterns", default=[])
    
    @property
    def output_format(self) -> str:
        """Get output format."""
        return self.get_value("output", "format", default="console")
    
    @property
    def show_progress(self) -> bool:
        """Get progress bar setting."""
        return self.get_value("output", "show_progress", default=True)
    
    @property
    def verbose(self) -> bool:
        """Get verbose output setting."""
        return self.get_value("output", "verbose", default=False)
    
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
            "high": self.get_value("thresholds", "complexity", "high", default=10)
        }
    
    @property
    def maintainability_thresholds(self) -> Dict[str, int]:
        """Get maintainability index threshold values."""
        return {
            "low": self.get_value("thresholds", "maintainability_index", "low", default=40),
            "medium": self.get_value("thresholds", "maintainability_index", "medium", default=60),
            "high": self.get_value("thresholds", "maintainability_index", "high", default=80)
        } 