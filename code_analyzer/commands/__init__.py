"""
Commands package for code analyzer.
"""

from .command_registry import registry
from .analyze import AnalyzeCommand

__all__ = ['registry', 'AnalyzeCommand'] 