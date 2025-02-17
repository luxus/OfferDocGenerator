from pathlib import Path
from typing import Dict, Any, List, TypedDict, NotRequired, Required, TypeVar, override, Self
from pydantic_settings import BaseSettings
from pydantic import field_validator, Field

class FolderStructure(TypedDict, total=True):
    templates: Required[Path]
    common: Required[Path]
    products: Required[Path]
    output: Required[Path]
    generated: Required[Path]

class ProductSection(TypedDict):
    name: str
    sections: List[str]
    variables: NotRequired[Dict[str, str]]

class FolderConfig(BaseSettings):
    templates: Path = Field(default=Path("templates"))
    common: Path = Field(default=Path("common"))
    products: Path = Field(default=Path("products"))
    output: Path = Field(default=Path("output"))
    generated: Path = Field(default=Path("generated"))

    model_config = {
        "frozen": True,
        "strict": True
    }

class Config(BaseSettings):
    output_dir: Path = Field(default=Path("tmp"))
    prefix: str = Field(default="Offer")
    base_path: Path = Field(default=Path.cwd())
    variables: Dict[str, Any] = Field(
        default_factory=lambda: {
            "customer": "Default Customer",
            "product_name": "",
            "currency": "EUR"
        }
    )
    folders: FolderConfig = Field(default_factory=FolderConfig)
    output_prefix: str = Field(default="DOC-")
    default_language: str = Field(default="en")
    supported_languages: List[str] = Field(
        default_factory=lambda: ["en", "de", "fr"]
    )
    products: List[ProductSection] = Field(default_factory=list)

    @field_validator('base_path', 'output_dir')
    @classmethod
    def validate_paths(cls, v: Path) -> Path:
        if isinstance(v, str):
            v = Path(v)
        v.mkdir(parents=True, exist_ok=True)
        return v.resolve()

    @override
    def model_copy(self, *, deep: bool = False) -> Self:
        return super().model_copy(deep=deep)
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(**data)

    model_config = {
        "arbitrary_types_allowed": True
    }
