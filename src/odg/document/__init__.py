"""Document handling module."""

from .base import BaseDocument
from .docx import DocxDocument
from .types import DocumentFormat, DocumentMode, SectionType
from .section import DocumentSection

__all__ = [
    'BaseDocument',
    'DocxDocument',
    'DocumentFormat',
    'DocumentMode',
    'SectionType',
    'DocumentSection',
]