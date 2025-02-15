from pydantic import BaseModel, Field, ValidationInfo, computed_field
from pydantic import field_validator, model_validator
from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml
import sys
import logging
from yaml.resolver import BaseResolver
import os

logger = logging.getLogger(__name__)

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

    @model_validator(mode='after')
    def validate_secure_paths(self) -> 'Settings':
        # Remove the existence check, keep symlink check
        for field in [self.products, self.common, self.output, self.templates]:
            if field.is_symlink():
                raise ValueError(f"Symbolic links not allowed in path: {field}")
        return self

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

class AppConfig(BaseModel):
    customer: CustomerConfig
    offer: OfferConfig
    settings: Settings
    sales: SalesConfig
    languages: List[str] = ["EN", "DE"]
    currencies: List[str] = ["CHF", "EUR"]
    bundles: Dict[str, BundleConfig] = Field(default_factory=dict)
    textblock_patterns: List[str] = [
        "{var_name}_{language}.docx",
        "{var_name}.docx"
    ]

    @model_validator(mode='before')
    @classmethod
    def resolve_settings_paths(cls, data: dict, info: ValidationInfo) -> dict:
        """Resolve relative paths in settings relative to config file location"""
        if not info.context:
            return data
        
        config_path = info.context.get("config_path")
        if config_path and 'settings' in data:
            base_dir = config_path.parent.resolve()
            settings_data = data['settings']
            
            for field in ['products', 'common', 'output', 'templates']:
                if field in settings_data:
                    raw_value = str(settings_data[field])
                    path = Path(raw_value)
                    
                    # Handle absolute paths specified in config
                    if path.is_absolute():
                        resolved_path = path.resolve()
                    else:
                        resolved_path = (base_dir / path).resolve()
                    
                    settings_data[field] = str(resolved_path)
            
            data['settings'] = settings_data
        return data

    @property
    def products_path(self) -> Path:
        return Path(self.settings.products)
        
    @property
    def common_path(self) -> Path:
        return Path(self.settings.common)
        
    @property 
    def templates_path(self) -> Path:
        return Path(self.settings.templates)
        
    @property
    def output_path(self) -> Path:
        return Path(self.settings.output)

def load_config(config_path: Path) -> AppConfig:
    """Load configuration from YAML file with security checks."""
    try:
        # Security checks
        max_size = 1024 * 1024  # 1MB limit
        if config_path.stat().st_size > max_size:
            raise ValueError(f"Config file too large (>1MB): {config_path}")
        
        if config_path.owner() != Path(__file__).owner():
            raise ValueError("Config file owner mismatch")

        # Restrict YAML types
        def restricted_load(stream):
            loader = yaml.SafeLoader(stream)
            # Remove potentially dangerous constructors
            del loader.yaml_constructors['tag:yaml.org,2002:python/object']
            del loader.yaml_constructors['tag:yaml.org,2002:python/object/apply']
            return loader.get_single_data()

        with open(config_path) as f:
            config_data = restricted_load(f)
            
        return AppConfig.model_validate(
            config_data, 
            context={"config_path": config_path}
        )
    except Exception as e:
        logger.error(f"Error loading config from {config_path}: {e}")
        if isinstance(e, (ValueError, TypeError)):
            raise
        sys.exit(1)
