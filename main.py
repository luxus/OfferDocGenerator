import os
from pathlib import Path
import yaml
from datetime import date
import shutil

class ConfigGenerator:
    def __init__(self, output_dir="tmp"):
        self.script_dir = Path(__file__).parent
        self.output_dir = self.script_dir / output_dir
        
        # Initialize or clean temp directory
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
        
        # Create fresh directory structure based on documentation
        self.output_dir.mkdir(exist_ok=True)
        for dir_name in ["templates", "common", "products"]:
            (self.output_dir / dir_name).mkdir(exist_ok=True)

    def generate_config(self) -> Path:
        """Generate config.yaml based on your documentation files"""
        config_data = {
            # From docs/configuration.md
            "offer": {
                "number": f"OFFER-{date.today().isoformat()}",
                "date": date.today().isoformat(),
                "validity": {"en": "30 days", "de": "30 Tage"}
            },
            # From docs/configuration/folder_structure.md
            "settings": {
                "base_path": str(self.output_dir),
                "templates": str(self.output_dir / "templates"),
                "common": str(self.output_dir / "common"),
                "products": str(self.output_dir / "products")
            },
            # From docs/configuration/internationalization.md
            "internationalization": {
                "default_language": "en",
                "supported_languages": ["en", "de", "fr"],
                "currency_format": "EUR"
            },
            "customer": {
                "name": "Test Company",
                "address": "123 Main St",
                "city": "Test City",
                "zip": "12345",
                "country": "Test Country"
            },
            "sales": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "+1 234 567 890"
            }
        }

        config_path = self.output_dir / "config.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)
        
        return config_path

    def validate_config(self, config_path: Path) -> bool:
        """Validate the generated config file"""
        try:
            with open(config_path, "r") as f:
                loaded_config = yaml.safe_load(f)
            
            # Verify required sections
            self._verify_required_keys(loaded_config)
            return True
            
        except Exception as e:
            print(f"Config validation failed: {e}")
            return False

    def _verify_required_keys(self, config_data):
        """Verify presence of required configuration keys"""
        required_keys = ["offer", "settings", "customer", "sales"]
        
        for key in required_keys:
            if key not in config_data:
                raise ValueError(f"Missing required key: {key}")
