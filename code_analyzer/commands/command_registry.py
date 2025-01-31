"""
Command registry for managing CLI commands
"""

from typing import Dict, Type, Optional
from pathlib import Path

from .base_command import BaseCommand

class CommandRegistry:
    """Registry for CLI commands"""
    
    def __init__(self):
        self._commands: Dict[str, Type[BaseCommand]] = {}
        self._config_root: Optional[Path] = None
    
    def register(self, name: str, command_class: Type[BaseCommand]) -> None:
        """Register a command"""
        if name in self._commands:
            raise ValueError(f"Command '{name}' already registered")
        self._commands[name] = command_class
    
    def get_command(self, name: str) -> BaseCommand:
        """Get a command instance by name"""
        if name not in self._commands:
            raise ValueError(f"Command '{name}' not found")
        
        command = self._commands[name]()
        if self._config_root:
            command._setup(self._config_root)
        return command
    
    def set_config_root(self, path: Path) -> None:
        """Set configuration root path for all commands"""
        self._config_root = path
    
    def list_commands(self) -> Dict[str, str]:
        """List all registered commands and their descriptions"""
        return {
            name: cmd.__doc__.split('\n')[0] if cmd.__doc__ else "No description"
            for name, cmd in self._commands.items()
        }

# Global command registry instance
registry = CommandRegistry() 