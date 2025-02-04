from pydantic import BaseModel, validator
from pathlib import Path
from typing import Dict, Any, List
import yaml
import sys
import logging

logger = logging.getLogger(__name__)

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

    @validator('format')
    def validate_format(cls, v):
        valid_formats = ['docx', 'dotx']
        if v.lower() not in valid_formats:
            raise ValueError(f"Invalid format. Must be one of {valid_formats}")
        return v.lower()

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
    """Load configuration from YAML file."""
    try:
        with open(config_path) as f:
            config_data = yaml.safe_load(f)
        return AppConfig(**config_data)
    except Exception as e:
        logger.error(f"Error loading config from {config_path}: {e}")
        if isinstance(e, (ValueError, TypeError)):
            raise
        sys.exit(1)
