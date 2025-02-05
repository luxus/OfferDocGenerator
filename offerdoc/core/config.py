from pydantic import BaseModel, Field, ValidationInfo
from pydantic import field_validator, model_validator
from pathlib import Path
from typing import Dict, Any, List
import yaml
import sys
import logging
from yaml.resolver import BaseResolver
import os

logger = logging.getLogger(__name__)

class SecuritySettings(BaseModel):
    max_template_size_mb: int = Field(default=10, gt=0, lt=100)
    allowed_file_types: List[str] = ['docx', 'dotx']
    enable_audit_log: bool = True
    allow_unsafe_templates: bool = False

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
    products: str
    common: str
    output: str
    templates: str
    format: str = "docx"
    filename_pattern: str = "Offer_{product}_{language}_{currency}_{date}.{format}"
    template_pattern: str = "base_{language}.docx"
    security: SecuritySettings = Field(default_factory=SecuritySettings)

    @field_validator('format')
    @classmethod
    def validate_format(cls, v: str, info: ValidationInfo) -> str:
        valid_formats = ['docx', 'dotx']
        if v.lower() not in valid_formats:
            raise ValueError(f"Invalid format. Must be one of {valid_formats}")
        return v.lower()

    @model_validator(mode='after')
    def validate_secure_paths(self) -> 'Settings':
        for field in ['products', 'common', 'output', 'templates']:
            path = Path(getattr(self, field)).resolve()
            if not path.exists():
                raise ValueError(f"Path does not exist: {path}")
            if path.is_symlink():
                raise ValueError("Symbolic links not allowed in paths")
            setattr(self, field, str(path))
        return self

class SalesConfig(BaseModel):
    name: str
    email: str
    phone: str

class AppConfig(BaseModel):
    customer: CustomerConfig
    offer: OfferConfig
    settings: Settings
    sales: SalesConfig
    languages: List[str] = ["EN", "DE"]
    currencies: List[str] = ["CHF", "EUR"]
    textblock_patterns: List[str] = [
        "{var_name}_{language}.docx",
        "{var_name}.docx"
    ]

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
            
        return AppConfig(**config_data)
    except Exception as e:
        logger.error(f"Error loading config from {config_path}: {e}")
        if isinstance(e, (ValueError, TypeError)):
            raise
        sys.exit(1)
