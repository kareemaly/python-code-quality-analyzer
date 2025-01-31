"""
Command registry for managing available commands
"""

from typing import Dict, Type, Any, Optional

from .analyze import AnalyzeCommand
from .base_command import BaseCommand


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

    def get_command(self, name: str, **options) -> Optional[BaseCommand]:
        """Get a command instance by name.

        Args:
            name (str): Command name
            **options: Additional options to pass to the command

        Returns:
            Optional[BaseCommand]: Command instance if found, None otherwise
        """
        command_class = self._commands.get(name)
        if command_class:
            return command_class(**options)
        return None


# Global registry instance
registry = CommandRegistry()
