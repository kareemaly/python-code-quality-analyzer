"""
Base analyzer class for all analyzers
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

@dataclass
class AnalysisResult:
    """Base class for analysis results"""
    timestamp: datetime
    analyzer_name: str
    status: str
    data: Dict[str, Any]
    error: Optional[str] = None

class BaseAnalyzer(ABC):
    """Base class for all analyzers"""
    
    def __init__(self, config_root: Optional[Path] = None):
        if config_root is None:
            config_root = Path.home() / "Library/Application Support/Cursor"
        self.config_root = Path(config_root)
        self.result: Optional[AnalysisResult] = None
    
    @abstractmethod
    def analyze(self) -> Dict[str, Any]:
        """Run analysis and return results"""
        pass
    
    def _create_result(self, data: Dict[str, Any], error: Optional[str] = None) -> AnalysisResult:
        """Create a standardized analysis result"""
        return AnalysisResult(
            timestamp=datetime.now(),
            analyzer_name=self.__class__.__name__,
            status="error" if error else "success",
            data=data,
            error=error
        )
    
    def _validate_paths(self) -> None:
        """Validate required paths exist"""
        if not self.config_root.exists():
            raise FileNotFoundError(f"Config root not found: {self.config_root}")
    
    def _read_json_file(self, path: Path) -> Dict[str, Any]:
        """Safely read and parse JSON file"""
        try:
            if path.exists():
                import json
                with open(path) as f:
                    return json.load(f)
        except Exception as e:
            raise ValueError(f"Error reading {path}: {e}")
        return {} 