"""Document type definitions."""

from enum import StrEnum, auto
from typing import TypeAlias, TypeVar

# Type definitions
DocxType: TypeAlias = 'Document'  # from docx import Document
T = TypeVar('T')

class DocumentFormat(StrEnum):
    """Supported document formats."""
    DOCX = auto()
    PDF = auto()
    HTML = auto()
    MARKDOWN = auto()

class DocumentMode(StrEnum):
    """Document generation modes."""
    TEMPLATE = auto()
    DRAFT = auto()
    FINAL = auto()

class SectionType(StrEnum):
    """Document section types."""
    INTRODUCTION = auto()
    OVERVIEW = auto()
    TECHNICAL = auto()
    LEGAL = auto()