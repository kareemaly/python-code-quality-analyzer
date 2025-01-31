"""
Command registry for managing available commands
"""

from typing import Dict, Type
from .base_command import BaseCommand
from .analyze import AnalyzeCommand

class CommandRegistry:
    """Registry for available commands"""
    
    def __init__(self):
        """Initialize the registry"""
        self._commands: Dict[str, Type[BaseCommand]] = {}
        self.register_command("analyze", AnalyzeCommand)
    
    def register_command(self, name: str, command_class: Type[BaseCommand]) -> None:
        """Register a new command.
        
        Args:
            name (str): Command name
            command_class (Type[BaseCommand]): Command class
            
        Raises:
            ValueError: If command already registered
        """
        if name in self._commands:
            raise ValueError(f"Command '{name}' already registered")
        self._commands[name] = command_class
    
    def get_command(self, name: str) -> BaseCommand:
        """Get a command instance by name.
        
        Args:
            name (str): Command name
            
        Returns:
            BaseCommand: Command instance
            
        Raises:
            KeyError: If command not found
        """
        if name not in self._commands:
            raise KeyError(f"Command '{name}' not found")
        return self._commands[name]()

# Global registry instance
registry = CommandRegistry()