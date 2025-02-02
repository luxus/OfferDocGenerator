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
    textblocks: Dict[str, Any]
    output: Dict[str, Any]
    customer: Dict[str, str]
    sales: Dict[str, str]

    def __post_init__(self):
        """Validate configuration after initialization."""
        required_fields = {
            'offer': ['sections', 'template', 'number', 'date', 'validity'],
            'textblocks': ['common', 'products_dir'],
            'output': ['folder'],
            'customer': ['name', 'address', 'city', 'zip', 'country'],
            'sales': ['name', 'email', 'phone']
        }

        for section, fields in required_fields.items():
            if not all(field in getattr(self, section) for field in fields):
                missing = [f for f in fields if f not in getattr(self, section)]
                raise ValueError(f"Missing required fields in {section}: {missing}")

def load_config(config_path: Path) -> Config:
    """Load configuration from YAML file."""
    try:
        with open(config_path) as f:
            config_data = yaml.safe_load(f)
            return Config(**config_data)
    except Exception as e:
        logger.error(f"Error loading config from {config_path}: {e}")
        sys.exit(1)

def get_product_names(textblock_dir: Path) -> List[str]:
    """Get list of available products from the textblock directory structure."""
    products_dir = textblock_dir / "products"
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

def load_textblocks(config: Config, sections: List[str], product_name: str, language: str) -> Dict[str, Any]:
    """Load textblocks as RichText objects preserving formatting."""
    textblocks = {}
    common_dir = Path(config.textblocks["common"]["folder"])
    product_dir = Path(config.textblocks["products_dir"]) / product_name

    # Use consistent lowercase filenames with proper language formatting
    lang_suffix = f"_{language.upper()}.docx"

    for section in sections:
        # Try product-specific textblock first
        product_file = product_dir / f"section_{section}{lang_suffix}"
        if product_file.exists():
            logger.info(f"Loading product-specific textblock for section {section} from {product_file}")
            doc = Document(str(product_file))
            rt = RichText()
            for para in doc.paragraphs:
                if para.text.strip():
                    for run in para.runs:
                        rt.add(run.text, bold=run.bold, italic=run.italic, underline=run.underline)
                    rt.add('\n')
            textblocks[f"section_{section}"] = rt
            continue

        # Fall back to common textblock
        common_file = common_dir / f"section_{section}{lang_suffix}"
        if common_file.exists():
            logger.info(f"Loading common textblock for section {section} from {common_file}")
            doc = Document(str(common_file))
            rt = RichText()
            for para in doc.paragraphs:
                if para.text.strip():
                    for run in para.runs:
                        rt.add(run.text, bold=run.bold, italic=run.italic, underline=run.underline)
                    rt.add('\n')
            textblocks[f"section_{section}"] = rt
            continue

        logger.warning(f"No textblock found for section {section} in language {language}")

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
    """Build the context with dynamic config variable resolution."""
    language = language.upper()
    return {
        "Config": config,  # Add full config reference
        "LANGUAGE": language,
        "PRODUCT": product_name,
        "CURRENCY": currency
    }

def render_offer(template_path: Path, context: Dict[str, Any], output_path: Path):
    """
    Renders the DOCX template with RichText content and saves the output.
    """
    if not template_path.exists():
        logger.error(f"Template file not found: {template_path}")
        sys.exit(1)

    try:
        # Use context manager for proper template handling
        with DocxTemplate(str(template_path)) as doc:
            # Get variables must be inside context manager block
            template_vars = doc.get_undeclared_template_vars()
            
            # Resolve variables from config
            config = context["Config"]
            for var in template_vars:
                if var not in context and not var.startswith('section_'):
                    try:
                        context[var] = resolve_config_variable(var, config)
                    except ValueError:
                        logger.warning(f"Variable {var} not found in config")

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

            # Render happens inside context manager
            doc.render(context, autoescape=True)
            
            # Ensure output directory exists
            output_path = output_path.with_suffix('.docx')
            output_path.parent.mkdir(parents=True, exist_ok=True)
            doc.save(str(output_path))
            logger.info(f"Offer document generated at: {output_path}")
            
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
    products = get_product_names(Path(config.textblocks["products_dir"]))
    if not products:
        logger.error("No products found in textblock directory")
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
                textblocks = load_textblocks(config, config.offer["sections"], product, lang)
                context.update(textblocks)

                # Get template path
                template_path = Path(config.offer["template"]) / f"base_{lang}.docx"
                if not template_path.exists():
                    logger.error(f"Missing template for {lang}: {template_path}")
                    continue

                # Generate output filename with currency
                output_file = Path(config.output["folder"]) / f"Offer_{product}_{lang}_{currency}.docx"
                
                # Render the offer document
                render_offer(template_path, context, output_file)

if __name__ == "__main__":
    main()
