"""Base document handling."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Protocol, Any, Sequence

class DocumentHandler(Protocol):
    """Protocol for document handlers."""
    def save(self, path: Path) -> None: ...
    def add_heading(self, text: str, level: int = 1) -> Any: ...
    def add_paragraph(self, text: str | None = None) -> Any: ...

class BaseDocument(ABC):
    """Base class for document handling."""
    
    @abstractmethod
    def create(self) -> DocumentHandler:
        """Create a new document."""
        raise NotImplementedError
    
    @abstractmethod
    def open(self, path: Path) -> DocumentHandler:
        """Open an existing document."""
        raise NotImplementedError
    
    @abstractmethod
    def merge(self, documents: Sequence[Path], output_path: Path) -> None:
        """Merge multiple documents into one."""
        raise NotImplementedError
    
    @abstractmethod
    def validate(self, path: Path) -> bool:
        """Validate document structure."""
        raise NotImplementedError