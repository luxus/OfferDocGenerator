"""Document section handling."""

from dataclasses import dataclass, field
from typing import List
from .types import SectionType

@dataclass(frozen=True, slots=True)
class DocumentSection:
    """Represents a document section with its content structure."""
    
    title: str
    subsections: List[str]
    variables: List[str] = field(default_factory=list)
    section_type: SectionType = field(default=SectionType.INTRODUCTION)