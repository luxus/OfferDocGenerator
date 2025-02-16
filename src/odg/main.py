import os
import argparse
from pathlib import Path
import yaml
from datetime import date
import shutil
from typing import Dict, Any
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH

VERSION = "1.0.0"

class ConfigGenerator:
    def __init__(self, output_dir: str = "tmp", is_validating: bool = False):
        self.script_dir = Path(__file__).parent
        self.output_dir = Path(output_dir).resolve()
        
        # Clean existing temp directory if it exists and KEEP_TMP is not set
        keep_tmp = os.getenv("KEEP_TMP", "False").lower() == "true"
        if self.output_dir.exists() and not keep_tmp and not is_validating:
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

    def create_docx_template(self, template_name: str = "base_en.docx") -> Path:
        """Create a basic DOCX template with placeholders"""
        try:
            # Ensure templates directory exists
            templates_dir = self.output_dir / "templates"
            templates_dir.mkdir(exist_ok=True)
            
            # Create the template file path
            template_path = templates_dir / template_name
            
            if template_path.exists():
                print(f"Template already exists: {template_path}")
                return template_path
            
            # Create a new Word document
            doc = Document()
            
            # Add title
            doc.add_heading("Base Offer Template", level=1)
            doc.add_paragraph("")
            
            # Add customer information section
            customer_section = doc.add_section()
            customer_para = doc.add_paragraph("Customer Information:")
            customer_para.style = 'Heading 2'
            customer_para.alignment = WD_ALIGN_PARAGRAPH.LEFT
            
            placeholders = [
                "customer_company",
                "customer_address",
                "sales_contact_name",
                "sales_contact_email",
                "offer_number",
                "validity_period"
            ]
            
            # Add placeholder fields
            for ph in placeholders:
                doc.add_paragraph(f"{{{{ {ph} }}}}")
            
            # Save the document
            doc.save(template_path)
            
            print(f"Created template file: {template_path}")
            return template_path
            
        except Exception as e:
            print(f"Error creating template: {e}")
            return None

    def create_sample_docx(self, template_name: str = "base_en.docx") -> Path:
        """Create a sample DOCX file from the template"""
        try:
            # Get the template path
            templates_dir = self.output_dir / "templates"
            template_path = templates_dir / template_name
            
            if not template_path.exists():
                print(f"Template not found: {template_path}")
                return None
                
            # Create a sample document in the output directory
            sample_output = (
                self.output_dir /
                "output" /
                f"sample_offer_{date.today().isoformat()}.docx"
            )
            
            # Copy template to sample output
            shutil.copy2(template_path, sample_output)
            
            print(f"Created sample document: {sample_output}")
            return sample_output
            
        except Exception as e:
            print(f"Error creating sample docx: {e}")
            return None

    @staticmethod
    def _clean_temp_directory(path):
        """Clean up temporary files unless KEEP_TMP is True"""
        keep_tmp = os.getenv("KEEP_TMP", "False").lower() == "true"
        
        if not keep_tmp:
            if isinstance(path, str):
                path = Path(path)
            
            if isinstance(path, Path) and path.exists():
                # Only remove temporary files, preserve existing config.yaml
                for item in path.iterdir():
                    if item.is_file() and item.name != "config.yaml":
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item, ignore_errors=True)

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

def _verify_required_keys(config_data):
    """Verify presence of required configuration keys"""
    required_keys = ["offer", "settings", "customer", "sales"]
    
    for key in required_keys:
        if key not in config_data:
            raise ValueError(f"Missing required key: {key}")

def validate_single_config(config_path: Path) -> bool:
    """Validate a single config.yaml file"""
    try:
        with open(config_path, "r") as f:
            loaded_config = yaml.safe_load(f)
        
        # Verify required sections
        _verify_required_keys(loaded_config)
        return True
            
    except Exception as e:
        print(f"Config validation failed: {e}")
        return False

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
            if not validate_single_config(config_file):
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

    # Create template command
    create_template_parser = subparsers.add_parser(
        'create-template',
        help='Create a base DOCX template with placeholders'
    )
    create_template_parser.add_argument(
        '--name', 
        type=str, 
        default="base_en.docx",
        help='Name of the template file (default: base_en.docx)'
    )

    # Create sample command
    create_sample_parser = subparsers.add_parser(
        'create-sample',
        help='Create a sample DOCX file from the template'
    )
    create_sample_parser.add_argument(
        '--template', 
        type=str, 
        default="base_en.docx",
        help='Name of the template file to use (default: base_en.docx)'
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

        # Ask user if they want to create template and sample files
        while True:
            prompt = "\nWould you like to create additional template files? (y/N) "
            create_template = input(prompt).lower().strip()
            
            if create_template == 'y':
                # Create the DOCX template
                print("\nCreating template file...")
                template_name = "base_en.docx"
                template_path = config_gen.create_docx_template(template_name)
                
                if not template_path:
                    print("Error creating template file.")
                    return 1
                
            elif create_template == 'n' or create_template == '':
                # Don't create any additional files
                pass
            
            else:
                print("\nPlease enter either 'y' or 'n'.")
                continue
            
            break

        # After optionally creating the template, ask about the sample file
        if create_template.lower() == 'y':
            while True:
                prompt = "\nWould you like to create a sample document using this template? (y/N) "
                create_sample = input(prompt).lower().strip()
                
                if create_sample == 'y':
                    # Create the sample DOCX file
                    print("\nCreating sample document...")
                    sample_template_name = "base_en.docx"
                    sample_path = config_gen.create_sample_docx(sample_template_name)
                    
                    if not sample_path:
                        print("Error creating sample document.")
                        return 1
                    
                elif create_sample == 'n' or create_sample == '':
                    # Don't create any additional files
                    pass
                
                else:
                    print("\nPlease enter either 'y' or 'n'.")
                    continue
                
                break

        print("\nProcess completed successfully!")
        return 0
    elif args.command == 'validate':
        output_dir = args.directory.resolve()
        
        # Validate all config files in directory
        if not validate_config_files(output_dir):
            print("Validation failed. See above errors.")
            return 1
        
        print("All configurations are valid!")
        return 0
    elif args.command == 'create-template':
        config_gen = ConfigGenerator()
        template_path = config_gen.create_docx_template(args.name)
        if not template_path:
            return 1
        return 0
    elif args.command == 'create-sample':
        config_gen = ConfigGenerator()
        sample_path = config_gen.create_sample_docx(args.template)
        if not sample_path:
            return 1
        return 0
    else:
        parser.print_help()
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
