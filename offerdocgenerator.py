#!/usr/bin/env python3
import sys
import logging
import traceback
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from docxtpl import DocxTemplate, RichText, InlineImage
from docx.shared import Pt, Mm
from docx import Document
import io
import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Config:
    """Configuration data loaded from YAML."""
    offer: Dict[str, Any]
    settings: Dict[str, Any]
    customer: Dict[str, str]
    sales: Dict[str, str]

    def __post_init__(self):
        """Validate configuration after initialization."""
        # First check required sections exist
        required_sections = ['offer', 'settings', 'customer', 'sales']
        missing_sections = [section for section in required_sections if not hasattr(self, section)]
        if missing_sections:
            raise ValueError(f"Missing required config sections: {missing_sections}")

        # Then check fields within each section
        required_fields = {
            'offer': ['number', 'date', 'validity'],
            'settings': ['products', 'common', 'output', 'template_prefix'],
            'customer': ['name', 'address', 'city', 'zip', 'country'],
            'sales': ['name', 'email', 'phone']
        }

        for section, fields in required_fields.items():
            if not all(field in getattr(self, section) for field in fields):
                missing = [f for f in fields if f not in getattr(self, section)]
                raise ValueError(f"Missing required fields in {section}: {missing}")
        
        # Validate output format if specified
        valid_formats = ['docx', 'dotx']
        output_format = self.settings.get('format', 'docx').lower()
        if output_format not in valid_formats:
            raise ValueError(f"Invalid output format. Must be one of {valid_formats}")

def load_config(config_path: Path) -> Config:
    """Load configuration from YAML file."""
    try:
        with open(config_path) as f:
            config_data = yaml.safe_load(f)
            
        # Validate required sections first
        required_sections = ['offer', 'textblocks', 'output', 'customer', 'sales']
        missing_sections = [s for s in required_sections if s not in config_data]
        if missing_sections:
            raise ValueError(f"Missing required config sections: {missing_sections}")
            
        # Create config instance and validate
        config = Config(**config_data)
        return config
        
    except Exception as e:
        logger.error(f"Error loading config from {config_path}: {e}")
        if isinstance(e, (ValueError, TypeError)):
            raise  # Re-raise validation errors for tests to catch
        sys.exit(1)

def get_product_names(config: Config) -> List[str]:
    """Get list of available products from the products directory."""
    products_dir = Path(config.settings["products"])
    if not products_dir.exists():
        logger.error(f"Products directory not found: {products_dir}")
        return []
    return [d.name for d in products_dir.iterdir() if d.is_dir()]

def load_textblock_file(file_path: Path) -> str:
    """
    Load content from a DOCX file.
    Returns the text content preserving paragraphs.
    """
    try:
        doc = Document(str(file_path))
        # Join paragraphs with double newlines to preserve formatting
        content = "\n\n".join(paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip())
        return content
    except Exception as e:
        logger.error(f"Error reading textblock file {file_path}: {e}")
        return ""

def _load_richtext(file_path: Path) -> RichText:
    """Load a DOCX file into a RichText object preserving formatting."""
    rt = RichText()
    try:
        doc = Document(str(file_path))
        for para in doc.paragraphs:
            if para.text.strip():
                for run in para.runs:
                    rt.add(run.text, 
                          bold=run.bold, 
                          italic=run.italic,
                          underline=run.underline)
                rt.add('\n')
    except Exception as e:
        logger.error(f"Error loading {file_path}: {e}")
    return rt

def load_textblocks(config: Config, product_name: str, language: str) -> Dict[str, Any]:
    """Dynamically load all textblocks from product and common directories."""
    textblocks = {}
    lang_suffix = f"_{language.upper()}.docx"
    
    # Load from common directory
    common_dir = Path(config.settings["common"])
    for file in common_dir.glob(f"section_*{lang_suffix}"):
        section = file.stem.replace(f"_{language.upper()}", "")
        textblocks[section] = _load_richtext(file)
    
    # Load from product directory (overrides common)
    product_dir = Path(config.settings["products"]) / product_name
    for file in product_dir.glob(f"section_*{lang_suffix}"):
        section = file.stem.replace(f"_{language.upper()}", "")
        textblocks[section] = _load_richtext(file)
    
    if not textblocks:
        logger.warning(f"No textblocks found for {product_name} in {language}")
        
    return textblocks

def resolve_config_variable(var_path: str, config: Config) -> Any:
    """Resolve dot-separated variable paths in the config structure."""
    current = config
    for part in var_path.split('.'):
        if isinstance(current, dict):
            current = current.get(part)
        elif hasattr(current, part):
            current = getattr(current, part)
        else:
            raise ValueError(f"Config path not found: {var_path}")
        if current is None:
            break
    return current

def build_context(config: Config, language: str, product_name: str, currency: str) -> Dict[str, Any]:
    """Build context with dynamic config structure access."""
    context = {
        "Config": config,
        "LANGUAGE": language.upper(),
        "PRODUCT": product_name,
        "CURRENCY": currency
    }
    
    # Dynamically flatten config structure
    def flatten_config(section: str, data: dict, prefix: str = ""):
        for key, value in data.items():
            if isinstance(value, dict):
                flatten_config(section, value, f"{prefix}{key}_")
            else:
                context_key = f"{prefix}{key}" if prefix else key
                context[f"{section}_{context_key}"] = value

    # Process all config sections
    for section in ["offer", "customer", "sales"]:
        if hasattr(config, section):
            flatten_config(section, getattr(config, section))

    return context

def render_offer(template_path: Path, context: Dict[str, Any], output_path: Path):
    """
    Renders the DOCX template with RichText content and saves the output.
    """
    if not template_path.exists():
        logger.error(f"Template file not found: {template_path}")
        sys.exit(1)

    try:
        # Initialize template directly
        doc = DocxTemplate(str(template_path))
        
        # Get template variables
        template_vars = doc.get_undeclared_template_variables()

        # Add textblocks to context
        textblocks = {k:v for k,v in context.items() if k.startswith('section_')}
        context.update(textblocks)

        # Convert any remaining Path objects to RichText
        for key, value in context.items():
            if isinstance(value, Path) and key.startswith('section_'):
                source_doc = Document(str(value))
                rt = RichText()
                for para in source_doc.paragraphs:
                    if para.text.strip():
                        for run in para.runs:
                            rt.add(run.text, bold=run.bold, italic=run.italic, underline=run.underline)
                        rt.add('\n')
                context[key] = rt

        # Render template
        doc.render(context, autoescape=True)
        
        # Handle different output formats
        output_format = output_path.suffix[1:].lower()
        
        if output_format == 'dotx':
            # Change content type for template format
            document_part = doc.docx.part
            document_part._content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.template.main+xml'
        
        # Ensure parent directories exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save with configured format
        doc.save(str(output_path))
        logger.info(f"Document generated at: {output_path}")
        
    except Exception as e:
        logger.error(f"Error during template rendering: {e}")
        logger.error(f"Error details: {traceback.format_exc()}")
        raise

def main():
    """Main entry point for the offer document generator."""
    if len(sys.argv) < 2:
        print("Usage: python offerdocgenerator.py <config.yaml>")
        sys.exit(1)

    # Use test_data config if running from tests
    if "test" in sys.argv[1].lower():
        test_data = Path(__file__).parent / "test_data"
        config_path = test_data / "test_config.yaml"
    else:
        config_path = Path(sys.argv[1])
    config = load_config(config_path)

    # Get available products
    products = get_product_names(config)
    if not products:
        logger.error("No products found in products directory")
        sys.exit(1)

    # Supported languages and currencies
    languages = ["EN", "DE"]
    currencies = ["CHF", "EUR"]
    
    # Generate offer documents for each combination
    for lang in languages:
        for currency in currencies:
            for product in products:
                # Build context with currency
                context = build_context(config, lang, product, currency)
                textblocks = load_textblocks(config, product, lang)
                context.update(textblocks)

                # Get template path using template prefix
                template_path = Path(config.settings["template_prefix"]) / f"base_{lang}.docx"
                if not template_path.exists():
                    logger.error(f"Missing template for {lang}: {template_path}")
                    continue

                # Create output directory (no language subdirectory)
                output_dir = Path(config.settings["output"]) / product
                output_dir.mkdir(parents=True, exist_ok=True)
                
                # Generate output filename with configurable prefix and format
                prefix = config.settings.get("prefix", "Offer_")
                fmt = config.settings.get("format", "docx")
                output_file = output_dir / f"{prefix}{product}_{lang}_{currency}.{fmt}"
                
                # Render the offer document
                render_offer(template_path, context, output_file)

if __name__ == "__main__":
    main()
