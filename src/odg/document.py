from typing import TypeAlias, LiteralString, Final, TypeGuard
from enum import StrEnum, auto
from dataclasses import dataclass

# Type aliases for domain-specific types
DocumentId: TypeAlias = str
TemplateName: TypeAlias = LiteralString
SectionName: TypeAlias = LiteralString

class DocumentType(StrEnum):
    OFFER = auto()
    CONTRACT = auto()
    PROPOSAL = auto()

@dataclass(frozen=True, slots=True)
class DocumentMetadata:
    id: DocumentId
    type: DocumentType
    template: TemplateName
    sections: list[SectionName]

    def is_valid_section(self, section: str) -> TypeGuard[SectionName]:
        return (
            isinstance(section, str) 
            and section in self.sections 
            and section.isascii()
        )

class DocumentValidator:
    REQUIRED_SECTIONS: Final[set[SectionName]] = {
        "introduction",
        "scope",
        "terms",
        "conditions"
    }

    def validate_metadata(self, metadata: DocumentMetadata) -> bool:
        missing = self.REQUIRED_SECTIONS - set(metadata.sections)
        if missing:
            raise ValueError(f"Missing required sections: {missing}")
        return True