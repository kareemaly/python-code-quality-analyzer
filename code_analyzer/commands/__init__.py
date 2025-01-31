"""
Commands package for code analyzer.
"""

from .analyze import AnalyzeCommand
from .command_registry import registry

__all__ = ["registry", "AnalyzeCommand"]
