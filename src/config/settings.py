from pathlib import Path
from typing import List, Dict
from pydantic_settings import BaseSettings
from pydantic import validator

class Config(BaseSettings):
    prefix: str = "Offer"
    base_path: Path = Path("./base")
    folders: Dict[str, Path] = {
        "templates": "./templates",
        "common": "./common",
        "products": "./products",
        "output": "./output"
    }
    output_prefix: str = "DOC-"
    default_language: str = "en"
    supported_languages: List[str] = ["en", "de", "fr"]
    
    @validator("base_path", "folders")
    def validate_paths(cls, v):
        if not v.exists():
            v.mkdir(parents=True, exist_ok=True)
        return v

    class Config:
        env_prefix = "offerdoc_"
