from pydantic import BaseModel, Field, ValidationInfo, computed_field
from pathlib import Path
from typing import Dict, Any, List, Optional

class BundleSecurity(BaseModel):
    max_products: int = Field(default=5, ge=1, le=10)
    max_discount: float = Field(default=30.0, ge=0, le=100)
    allow_cross_references: bool = False

class SecuritySettings(BaseModel):
    max_template_size_mb: int = Field(default=10, gt=0, lt=100)
    allowed_file_types: List[str] = ['docx', 'dotx']
    enable_audit_log: bool = True
    allow_unsafe_templates: bool = False
    bundles: BundleSecurity = Field(default_factory=BundleSecurity)
    max_merged_files: int = Field(default=10, ge=1, le=50)
    allow_section_overwriting: bool = False

class CustomerConfig(BaseModel):
    name: str
    address: str
    city: str
    zip: str
    country: str

class OfferConfig(BaseModel):
    number: str
    date: str
    validity: Dict[str, str]

class Settings(BaseModel):
    products: Path = Field(..., description="Path to product-specific templates")
    common: Path = Field(..., description="Path to common assets directory")
    output: Path = Field(..., description="Output directory for generated documents")
    templates: Path = Field(..., description="Template directory path")
    format: str = "docx"
    filename_pattern: str = "Offer_{product}_{language}_{currency}_{date}.{format}"
    template_pattern: str = "base_{language}.docx"
    security: SecuritySettings = Field(default_factory=SecuritySettings)

    @computed_field
    @property
    def output_path(self) -> Path:
        """Get resolved output path"""
        return Path(self.output).resolve()

    @field_validator('format')
    @classmethod
    def validate_format(cls, v: str, info: ValidationInfo) -> str:
        valid_formats = ['docx', 'dotx']
        if v.lower() not in valid_formats:
            raise ValueError(f"Invalid format. Must be one of {valid_formats}")
        return v.lower()

class SalesConfig(BaseModel):
    name: str
    email: str
    phone: str
    contacts: List[Dict[str, str]] = Field(default_factory=list)

class BundleConfig(BaseModel):
    name: str
    products: List[str]
    discount: Dict[str, float] = {"percentage": 0.0}
    template: Optional[str] = None
    variables: Dict[str, Any] = Field(default_factory=dict)
