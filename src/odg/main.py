import os
import argparse
import logging
import tempfile
from pathlib import Path
import yaml
from datetime import date
import shutil
from typing import Dict, Any, List
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docxtpl import DocxTemplate
from docx.shared import Pt
from jinja2 import Environment, FileSystemLoader, Template

VERSION = "1.0.0"

# Configure logging with more detailed format
logger = logging.getLogger(__name__)

def setup_logging():
    # Only set up logging if we're not in a testing environment
    if os.getenv("TESTING") != "True":
        # Ensure only one handler is added to the logger
        if not logger.handlers:
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.DEBUG)

setup_logging()

class ConfigGenerator:
    def __init__(self, output_dir: str = "tmp"):
        self.output_dir = Path(output_dir).resolve()
        logger.debug(f"Initializing ConfigGenerator with output_dir: {self.output_dir}")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_config(self) -> Path:
        """Generate config.yaml based on documentation files"""
        logger.debug(f"Generating config in: {self.output_dir}")
        
        # Create necessary directories
        logger.debug(f"Creating subdirectories in: {self.output_dir}")
        for subdir in ["templates", "common", "products", "output", "generated"]:
            dir_path = self.output_dir / subdir
            if not dir_path.exists():
                logger.debug(f"Creating directory: {dir_path}")
                dir_path.mkdir(parents=True, exist_ok=True)
            else:
                logger.debug(f"Directory already exists: {dir_path}")

        config_data: Dict[str, Any] = {
            "offer": {
                "number": f"OFFER-{date.today().isoformat()}",
                "date": date.today().isoformat(),
                "validity": {"en": "30 days", "de": "30 Tage"}
            },
            # From docs/configuration/folder_structure.md
            "settings": {
                "base_path": str(self.output_dir),
                "folders": {
                    "templates": "./templates",
                    "common": "./common",
                    "products": "./products",
                    "output": "./output",
                    "generated": "./generated"
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
            },
            "products": [{
                "name": "Web Application Security Assessment",
                "sections": [
                    "Introduction",
                    "Product Overview", 
                    "Technical Specifications"
                ]
            }]
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
            templates_dir = self.output_dir / "templates"
            templates_dir.mkdir(exist_ok=True)
            
            template_path = templates_dir / template_name
            
            # Always create a new template to ensure it has the correct structure
            doc = Document()
            
            # Add title and basic structure with proper styling
            title = doc.add_heading("Base Offer Template", level=1)
            title.runs[0].font.size = Pt(16)
            
            # Add required sections for base template
            doc.add_heading("Introduction", level=1)
            doc.add_paragraph("Introduction content goes here...")
            
            doc.add_heading("General Information", level=1)
            doc.add_paragraph("General information content goes here...")
            
            # Customer Information section
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
            
            for ph in placeholders:
                doc.add_paragraph(f"{{{{ {ph} }}}}")
            
            # Add Introduction section
            doc.add_heading("Introduction", level=1)
            doc.add_paragraph("Introduction content goes here...")
            
            # Load config data
            config_path = self.output_dir / "config.yaml"
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config_data = yaml.safe_load(f)

                # Add sections based on document type and config
                if "product" in template_name.lower():
                    # Always include required product sections
                    required_sections = ["Introduction", "Product Overview", "Technical Specifications"]
                    
                    # Get additional sections from config if available
                    if "products" in config_data and config_data["products"]:
                        product = config_data["products"][0]
                        if "sections" in product:
                            required_sections.extend([s for s in product["sections"] if s not in required_sections])
                    
                    for section in required_sections:
                        if section != "Introduction":  # Already added above
                            doc.add_heading(section, level=1)
                            doc.add_paragraph(f"{section} content goes here...")
                else:
                    # Default sections for non-product templates
                    doc.add_heading("General Information", level=1)
                    doc.add_paragraph("General information content goes here...")
                    doc.add_heading("Technical Specifications", level=1)
            
            # Add numbered list with proper nesting
            doc.add_paragraph("First item", style='List Number')
            doc.add_paragraph("First sub-item", style='List Number 2')
            doc.add_paragraph("Second sub-item", style='List Number 2')
            doc.add_paragraph("Second item", style='List Number')
            doc.add_paragraph("Third item", style='List Number')
            doc.add_paragraph("Third sub-item", style='List Number 2')
            
            doc.save(template_path)
            
            logger.info(f"Created template file: {template_path}")
            return template_path
            
        except Exception as e:
            logger.error(f"Error creating template: {e}")
            return None

    def merge_docx_files(self, input_paths: List[Path], output_path: Path, context: Dict[str, Any] = None) -> None:
        """Merge multiple DOCX files into a single document with continuous numbering."""
        merged_document = Document()

        for path in input_paths:
            # If the input is a template, render it first
            if str(path).endswith('.docx'):
                if context:
                    doc_template = DocxTemplate(str(path))
                    with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp:
                        doc_template.render(context)
                        doc_template.save(tmp.name)
                        sub_doc = Document(tmp.name)
                    os.unlink(tmp.name)
                else:
                    sub_doc = Document(path)
                
                for element in sub_doc.element.body:
                    merged_document.element.body.append(element)

        # Ensure continuous section numbering
        self._update_section_numbering(merged_document)

        # Save the merged document
        merged_document.save(output_path)
        logger.info(f"Merged document saved to {output_path}")

    def _update_section_numbering(self, doc: Document) -> None:
        """Update section headings to ensure continuous numbering."""
        current_section = 0
        sub_section_count = 0

        for paragraph in doc.paragraphs:
            if paragraph.style.name.startswith("Heading"):
                level = int(paragraph.style.name.split()[-1])
                
                # Extract the original text without numbering
                original_text = paragraph.text.split('.')[-1].strip()
                
                if level == 1:
                    current_section += 1
                    sub_section_count = 0
                    new_heading = f"{current_section}. {original_text}"
                elif level == 2:
                    sub_section_count += 1
                    new_heading = f"{current_section}.{sub_section_count}. {original_text}"
                else:
                    # Higher levels remain unchanged
                    continue
                
                paragraph.text = new_heading

    def create_sample_docx(self, product_name: str, language: str, currency: str) -> Path:
        """Create a sample DOCX file from the template with structured content."""
        try:
            generated_dir = self.output_dir / "generated"
            generated_dir.mkdir(exist_ok=True)
            
            # Load config data
            config_path = self.output_dir / "config.yaml"
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            
            # Determine base template based on language
            base_template_name = f"base_{language}.docx"
            templates_dir = self.output_dir / "templates"
            base_template_path = templates_dir / base_template_name
            
            if not base_template_path.exists():
                # Create a dummy base template for testing purposes
                doc = Document()
                doc.add_heading("Dummy Base Template", level=1)
                doc.save(base_template_path)
            
            # Collect product-specific sections from the products directory
            product_sections_dir = self.output_dir / "products" / product_name
            if not product_sections_dir.exists():
                product_sections_dir.mkdir(parents=True, exist_ok=True)
            product_sections = list(product_sections_dir.glob("*.docx"))
            
            input_paths = [base_template_path] + product_sections
            
            # Build comprehensive context from config
            context = {
                "customer_company": config_data["customer"]["name"],
                "customer_address": config_data["customer"]["address"],
                "sales_contact_name": config_data["sales"]["name"],
                "sales_contact_email": config_data["sales"]["email"],
                "offer_number": config_data["offer"]["number"],
                "validity_period": config_data["offer"]["validity"]["en"],
                "config": config_data,  # Pass entire config for flexible templating
                "date": date.today().isoformat()
            }
            
            # Add any additional dynamic variables
            if "variables" in config_data:
                context.update(config_data["variables"])
                
            # Load the template using DocxTemplate
            template = DocxTemplate(base_template_path)
            
            # Render the template with context
            template.render(context)
            
            # Convert to Document for additional modifications
            doc = Document(base_template_path)
            
            # Add all required sections based on template type
            if "product" in template_name.lower():
                required_sections = ["Introduction", "Product Overview", "Technical Specifications"]
                
                # Get additional sections from config if available
                if "products" in config_data and config_data["products"]:
                    product = config_data["products"][0]
                    if "sections" in product:
                        required_sections.extend([s for s in product["sections"] if s not in required_sections])
                
                for section in required_sections:
                    doc.add_heading(section, level=1)
                    doc.add_paragraph(f"{section} content goes here...")
            else:
                doc.add_heading("General Information", level=1)
                doc.add_paragraph("General information content goes here...")
                doc.add_heading("Technical Specifications", level=1)
                doc.add_paragraph("Technical specifications content goes here...")
            
            # Add numbered list with nested items
            paragraph = doc.add_paragraph("First item", style='List Number')
            sub_paragraph = doc.add_paragraph("Sub-item 1", style='List Number 2')
            paragraph = doc.add_paragraph("Second item", style='List Number')
            
            # Add bullet points with nested items
            bullet_para = doc.add_paragraph("Bullet Point 1", style='List Bullet')
            sub_bullet_para = doc.add_paragraph("Sub-bullet 1", style='List Bullet 2')
            
            sample_output = generated_dir / f"sample_{template_name}"
            doc.save(sample_output)
            
            print(f"Created sample document: {sample_output}")
            return sample_output
            
        except Exception as e:
            print(f"Error creating sample docx: {e}")
            raise


# Helper function to create base directory structure
def setup_default_folders(output_dir: Path = None):
    """Create default folder structure for quick setup"""
    if not output_dir:
        output_dir = Path.cwd() / "tmp"
        logger.debug(f"Using default output directory: {output_dir}")
    
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

        # Automatically create template and sample files
        try:
            # Create the DOCX template
            print("\nCreating template file...")
            template_name = "base_en.docx"
            template_path = config_gen.create_docx_template(template_name)
            
            if not template_path:
                print("Error creating template file.")
                return 1
            
            # Create sample document using the template
            print("\nCreating sample document...")
            sample_path = config_gen.create_sample_docx(template_name)
            if not sample_path:
                print("Error creating sample document.")
                return 1
            
        except Exception as e:
            print(f"An error occurred: {e}")
            return 1
        
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
