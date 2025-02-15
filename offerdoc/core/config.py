from pathlib import Path
from typing import Dict, Any, Optional
from .config.base import BaseConfig, SecuritySettings
from .exceptions import InvalidConfigError
import yaml
import logging

logger = logging.getLogger(__name__)

class AppConfig(BaseConfig):
    """Application configuration with validation and path resolution"""
    settings: SecuritySettings
    templates_path: Path
    products_path: Path
    output_path: Path
    
    @classmethod
    def load(cls, config_path: Path) -> 'AppConfig':
        """Load and validate configuration from YAML"""
        try:
            if not config_path.exists():
                raise InvalidConfigError(f"Config file not found: {config_path}")
                
            with open(config_path) as f:
                data = yaml.safe_load(f)
                
            instance = cls.from_dict(data)
            instance.validate_paths()
            return instance
            
        except Exception as e:
            logger.error(f"Failed to load config from {config_path}: {e}")
            raise InvalidConfigError(str(e))

    def get_template_path(self, language: str) -> Path:
        """Get template path with validation"""
        path = self.templates_path / f"template_{language}.docx"
        if not path.exists():
            raise InvalidConfigError(f"Template not found: {path}")
        return path

__all__ = ['AppConfig']
