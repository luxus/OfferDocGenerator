from pathlib import Path
from typing import List, Dict
from pydantic_settings import BaseSettings
from pydantic import field_validator

class Config(BaseSettings):
    output_dir: Path = Path("./tmp")
    prefix: str = "Offer"
    base_path: Path = Path("./base")
    variables: Dict[str, Any] = {}  # For custom template variables
    folders: Dict[str, Path] = {
        "templates": "./templates",
        "common": "./common",
        "products": "./products",
        "output": "./output"
    }
    output_prefix: str = "DOC-"
    default_language: str = "en"
    supported_languages: List[str] = ["en", "de", "fr"]
    
    @field_validator('base_path', 'folders', mode='before')
    def validate_paths(cls, v):
        if isinstance(v, dict):  # Handle folders as a dictionary
            for key, path in v.items():
                path = Path(path)
                if not path.exists():
                    path.mkdir(parents=True, exist_ok=True)
            return v
        else:
            path = Path(v)
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
            return v

    model_config = {
        "env_prefix": "offerdoc_"
    }
