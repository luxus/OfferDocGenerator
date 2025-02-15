import yaml
import logging
from pathlib import Path
from typing import Any
from .models import AppConfig
from ..errors.exceptions import InvalidConfigError

logger = logging.getLogger(__name__)

def load_config(config_path: Path) -> AppConfig:
    """Load configuration from YAML file with security checks."""
    try:
        # Security checks
        max_size = 1024 * 1024  # 1MB limit
        if config_path.stat().st_size > max_size:
            raise InvalidConfigError(f"Config file too large (>1MB): {config_path}")
        
        if config_path.owner() != Path(__file__).owner():
            raise InvalidConfigError("Config file owner mismatch")

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
            raise InvalidConfigError(str(e))
        raise
