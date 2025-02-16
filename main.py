import os
import argparse
from pathlib import Path
import yaml
from datetime import date
import shutil
from typing import Dict, Any

VERSION = "1.0.0"

class ConfigGenerator:
    def __init__(self, output_dir: str = "tmp"):
        self.script_dir = Path(__file__).parent
        self.output_dir = Path(output_dir).resolve()
        
        # Clean existing temp directory if it exists and KEEP_TMP is not set
        keep_tmp = os.getenv("KEEP_TMP", "False").lower() == "true"
        if self.output_dir.exists() and not keep_tmp:
            self._clean_temp_directory(self.output_dir)
        
        # Create fresh directory structure based on documentation
        self.output_dir.mkdir(exist_ok=True)
        for dir_name in ["templates", "common", "products", "output"]:
            (self.output_dir / dir_name).mkdir(exist_ok=True)

    def generate_config(self) -> Path:
        """Generate config.yaml based on documentation files"""
        config_data: Dict[str, Any] = {
            "offer": {
                "number": f"OFFER-{date.today().isoformat()}",
                "date": date.today().isoformat(),
                "validity": {"en": "30 days", "de": "30 Tage"}
            },
            # From docs/configuration/folder_structure.md
            "settings": {
                "base_path": str(self.output_dir.resolve()),
                "folders": {
                    "templates": "./templates",
                    "common": "./common",
                    "products": "./products",
                    "output": "./output"
                },
                "output_prefix": "DOC-"
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

    @staticmethod
    def _clean_temp_directory(path):
        """Clean up temporary files unless KEEP_TMP is True"""
        keep_tmp = os.getenv("KEEP_TMP", "False").lower() == "true"
        
        if not keep_tmp:
            if isinstance(path, str):
                path = Path(path)
            
            if isinstance(path, Path) and path.exists():
                shutil.rmtree(path, ignore_errors=True)

# Helper function to create base directory structure
def setup_default_folders(output_dir: Path = None):
    """Create default folder structure for quick setup"""
    if not output_dir:
        output_dir = Path(__file__).parent / "tmp"
    
    # Create main directories
    output_dir.mkdir(exist_ok=True)
    (output_dir / "templates").mkdir(exist_ok=True)
    (output_dir / "common").mkdir(exist_ok=True)
    (output_dir / "products").mkdir(exist_ok=True)
    (output_dir / "output").mkdir(exist_ok=True)

    # Create example product folder
    example_product = output_dir / "products" / "Web Application Security Assessment"
    example_product.mkdir(parents=True, exist_ok=True)

    print(f"Default structure created at: {output_dir}")

def validate_config_files(directory: Path):
    """Validate all config.yaml files in specified directory and subdirectories"""
    
    # Find all config.yaml files recursively
    config_files = list(directory.rglob("config.yaml"))
    
    if not config_files:
        print(f"No config.yaml files found in {directory}")
        return True
    
    # Validate each file
    for config_file in config_files:
        print(f"Validating {config_file}...")
        try:
            # Create a temporary ConfigGenerator instance with the same directory
            output_dir = config_file.parent
            config_gen = ConfigGenerator(output_dir=str(output_dir))
            
            if not config_gen.validate_config(config_file):
                print(f"Validation failed for: {config_file}")
                return False
                
            print(f"Successfully validated: {config_file}")
        except Exception as e:
            print(f"Error validating {config_file}: {e}")
            return False
            
    return True

def main():
    """Main entry point for the ODG CLI tool"""
    parser = argparse.ArgumentParser(
        description='Offer Document Generator (ODG) CLI Tool',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''
        Example usage:
          odg create my_project
          odg --help
          odg --version
        '''
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'odg {VERSION}',
        help='Show program version and exit'
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create a new project structure')
    create_parser.add_argument(
        'output_dir',
        type=str,
        help='Directory where the project structure will be created'
    )

    # Validate command
    validate_parser = subparsers.add_parser(
        'validate',
        help='Validate config.yaml files in specified directory'
    )
    validate_parser.add_argument(
        'directory',
        type=Path,
        nargs='?',  # Make it optional
        default=Path.cwd(),
        help='Directory to search for config.yaml (default: current directory)'
    )

    args = parser.parse_args()
    
    if args.command == 'create':
        output_dir = Path(args.output_dir).resolve()
        
        # Ensure the output directory exists
        output_dir.mkdir(exist_ok=True)
        
        # Create configuration generator instance
        config_gen = ConfigGenerator(output_dir=str(output_dir))
        
        # Generate and save config file
        config_path = config_gen.generate_config()
        
        # Print success message
        print(f"Created project structure in: {output_dir}")
        print("Included files and folders:")
        for root, dirs, files in os.walk(output_dir):
            level = root.replace(str(output_dir), '').count(os.sep)
            indent = '    ' * (level - 1) if level > 0 else ''
            print(f"{indent}{'├──' if dirs or files else '└──'} {Path(root).name}")
            
        # Validate the generated config
        if not config_gen.validate_config(config_path):
            print("Config validation failed. Please check your configuration.")
            return 1
        return 0
    elif args.command == 'validate':
        output_dir = args.directory.resolve()
        
        # Validate all config files in directory
        if not validate_config_files(output_dir):
            print("Validation failed. See above errors.")
            return 1
        
        print("All configurations are valid!")
        return 0
    else:
        parser.print_help()
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
