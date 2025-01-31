from dataclasses import dataclass
from pathlib import Path

@dataclass
class ComplexFunction:
    name: str
    complexity: int
    location: Path 