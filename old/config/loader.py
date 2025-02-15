import yaml
import logging
from pathlib import Path
from typing import Dict, Any
from ..exceptions import InvalidConfigError

logger = logging.getLogger(__name__)

def load_yaml_safely(path: Path) -> Dict[str, Any]:
    """Load YAML with security restrictions"""
    max_size = 1024 * 1024  # 1MB limit
    
    if path.stat().st_size > max_size:
        raise InvalidConfigError(f"Config file too large (>1MB): {path}")
        
    if path.owner() != Path(__file__).owner():
        raise InvalidConfigError("Config file owner mismatch")

    # Create restricted loader
    def restricted_load(stream):
        loader = yaml.SafeLoader(stream)
        # Remove dangerous constructors
        del loader.yaml_constructors['tag:yaml.org,2002:python/object']
        del loader.yaml_constructors['tag:yaml.org,2002:python/object/apply']
        return loader.get_single_data()

    try:
        with open(path) as f:
            return restricted_load(f)
    except Exception as e:
        raise InvalidConfigError(f"Failed to load YAML: {e}")
