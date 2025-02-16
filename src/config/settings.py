from pathlib import Path
from typing import List
from pydantic import BaseSettings, validator

class Config(BaseSettings):
    prefix: str = "Offer"
    base_path: Path = Path("./base")
    templates_path: Path = base_path / "templates"
    common_path: Path = base_path / "common" 
    products_path: Path = base_path / "products"
    output_path: Path = base_path / "output"

    default_language: str = "en"
    supported_languages: List[str] = ["en", "de", "fr"]
    
    @validator("base_path", "templates_path", "common_path", "products_path", "output_path")
    def validate_paths(cls, v):
        if not v.exists():
            v.mkdir(parents=True, exist_ok=True)
        return v

    class Config:
        env_prefix = "offerdoc_"
