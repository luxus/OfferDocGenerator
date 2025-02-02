#!/usr/bin/env python3
import sys
import logging
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

    def __post_init__(self):
        """Validate configuration after initialization."""
        required_fields = {
            'offer': ['sections', 'template'],
            'textblocks': ['common', 'products_dir'],
            'output': ['folder']
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

    for section in sections:
        # Try product-specific textblock first
        product_file = product_dir / f"Section_{section}{language}.docx"
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
        common_file = common_dir / f"Section_{section}{language}.docx"
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

def build_context(config: Config, language: str, product_name: str) -> Dict[str, Any]:
    """Build the context for template rendering."""
    # Ensure language code is uppercase for consistency with filenames
    language = language.upper()
    context = {
        "Offer": {
            "number": "2025-001",
            "date": "2025-02-02",
            "validity": "30 days"
        },
        "Customer": {
            "name": "Example Corp",
            "address": "123 Example Street",
            "city": "Example City",
            "zip": "12345",
            "country": "Example Country"
        },
        "Sales": {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "+1 234 567 890"
        },
        "LANGUAGE": language,
        "PRODUCT": product_name
    }
    return context

def render_offer(template_path: Path, context: Dict[str, Any], output_path: Path):
    """
    Renders the DOCX template with RichText content and saves the output.
    """
    if not template_path.exists():
        logger.error(f"Template file not found: {template_path}")
        sys.exit(1)

    try:
        # Create DocxTemplate instance
        doc = DocxTemplate(str(template_path))

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

        # Render the template with the context
        doc.render(context, autoescape=True)

        # Ensure the output directory exists
        output_path = output_path.with_suffix('.docx')
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save the rendered document
        doc.save(str(output_path))
        logger.info(f"Offer document generated at: {output_path}")
    except Exception as e:
        logger.error(f"Error during template rendering: {e}")
        logger.error(f"Error details: {str(e)}")
        raise

def main():
    """Main entry point for the offer document generator."""
    if len(sys.argv) < 2:
        print("Usage: python offerdocgenerator.py <config.yaml>")
        sys.exit(1)

    config_path = Path(sys.argv[1])
    config = load_config(config_path)

    # Get available products
    products = get_product_names(Path(config.textblocks["products_dir"]))
    if not products:
        logger.error("No products found in textblock directory")
        sys.exit(1)

    # For each language and product, generate an offer document
    for language in ["en", "de", "fr", "es", "it", "nl", "pt", "zh", "ja", "ko", "ar", "ru", "he", "hi", "th", "vi", "id", "ms", "tr", "pl", "cs", "sk", "hu", "ro", "bg", "el", "da", "fi", "no", "sv", "uk", "hr", "sr", "sl", "lt", "lv", "et", "mt", "cy", "ga", "gd", "gv", "kw", "br", "eu", "ca", "gl", "oc", "wa", "fur", "sc", "co", "lij", "lmo", "nap", "pms", "rm", "szl", "wo", "an", "ast", "lld", "mwl", "pcd", "vro", "zea", "frp", "gcf", "ht", "kea", "ksh", "lb", "mg", "mfe", "mhr", "mnc", "mwl", "myv", "nds", "nov", "pfl", "pms", "pt", "qu", "rgn", "rm", "rmy", "scn", "sco", "stq", "szl", "tet", "tpi", "vec", "vls", "vmf", "vot", "wa", "wae", "wep", "wuu", "xmf", "yrl", "zea"]:
        for product in products:
            # Build context with variables and textblocks
            context = build_context(config, language, product)
            textblocks = load_textblocks(config, config.offer["sections"], product, language)
            context.update(textblocks)

            # Get template path for current language
            template_path = Path(config.offer["template"]) / f"base_{language}.docx"
            if not template_path.exists():
                logger.error(f"Template not found for language {language}: {template_path}")
                continue

            # Generate output path
            output_file = Path(config.output["folder"]) / f"Offer_{product}_{language}.docx"
            
            # Render the offer document
            render_offer(template_path, context, output_file)

if __name__ == "__main__":
    main()
