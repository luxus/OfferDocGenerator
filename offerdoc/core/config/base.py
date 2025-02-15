from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, ValidationInfo, computed_field, field_validator

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

class BaseConfig(BaseModel):
    """Base configuration class with common validation logic"""
    model_config = {"validate_assignment": True}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseConfig':
        """Create instance from dictionary with validation"""
        return cls.model_validate(data)

    def validate_paths(self) -> None:
        """Validate all path fields exist"""
        for field_name, field_value in self.model_fields.items():
            if isinstance(field_value, Path):
                if not field_value.exists():
                    raise ValueError(f"Path does not exist: {field_value}")
