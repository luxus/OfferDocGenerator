#!/usr/bin/env python3
import sys
import logging
import traceback
from pathlib import Path

COLOR = {
    'HEADER': '\033[95m',
    'BLUE': '\033[94m',
    'CYAN': '\033[96m',
    'GREEN': '\033[92m',
    'YELLOW': '\033[93m',
    'RED': '\033[91m',
    'ENDC': '\033[0m',
    'BOLD': '\033[1m',
    'UNDERLINE': '\033[4m'
}

def colorize(text: str, color: str) -> str:
    """Wrap text in ANSI color codes if output is a terminal"""
    if sys.stdout.isatty():
        return f"{COLOR[color.upper()]}{text}{COLOR['ENDC']}"
    return text
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Set, Tuple
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
    offer: Dict[str, Any] = field(default_factory=dict)
    settings: Dict[str, Any] = field(default_factory=dict)
    customer: Dict[str, str] = field(default_factory=dict)
    sales: Dict[str, str] = field(default_factory=dict)
    
    @property
    def products_path(self) -> Path:
        return Path(self.settings["products"])
        
    @property
    def common_path(self) -> Path:
        return Path(self.settings["common"])
        
    @property 
    def templates_path(self) -> Path:
        return Path(self.settings["templates"])
        
    @property
    def output_path(self) -> Path:
        return Path(self.settings["output"])

    def __post_init__(self):
        """Validate configuration after initialization."""
        # Check for missing entire sections
        required_sections = ['offer', 'settings', 'customer', 'sales']
        missing_sections = [
            section for section in required_sections 
            if not getattr(self, section)  # Check if section is empty
        ]
        if missing_sections:
            raise ValueError(f"Missing required config sections: {missing_sections}")

        # Check fields within each section
        required_fields = {
            'offer': ['number', 'date', 'validity'],
            'settings': ['products', 'common', 'output', 'templates'],
            'customer': ['name', 'address', 'city', 'zip', 'country'],
            'sales': ['name', 'email', 'phone']
        }

        missing_fields = []
        for section, fields in required_fields.items():
            section_data = getattr(self, section, {})
            current_missing = [f for f in fields if f not in section_data]
            if current_missing:
                missing_fields.append(f"Missing required fields in {section}: {sorted(current_missing)}")

        if missing_fields:
            raise ValueError("\n".join(missing_fields))
        
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

def load_textblock(section: str, config: Config, product_name: str, language: str) -> Tuple[Optional[RichText], Optional[Path]]:
    """Dynamically load a textblock from product/common directories"""
    lang_suffix = f"_{language.upper()}.docx"
    paths = [
        config.products_path / product_name / f"{section}{lang_suffix}",
        config.products_path / product_name / f"{section}.docx",
        config.common_path / f"{section}{lang_suffix}",
        config.common_path / f"{section}.docx"
    ]
    
    for path in paths:
        if path.exists():
            return _load_richtext(path), path
    return None, None

def resolve_template_variables(template_vars: Set[str], config: Config, 
                            product_name: str, language: str) -> Dict[str, Any]:
    """Resolve variables from config, textblocks, and special handlers"""
    resolved = {}
    language = language.upper()
    
    print(colorize(f"\n🔎 Discovering sources for {len(template_vars)} template variables:", 'CYAN'))
    
    for var in template_vars:
        # Try direct config access first
        try:
            resolved[var] = resolve_config_variable(var, config)
            print(f"  {colorize(var.ljust(20), 'GREEN')} {colorize('← config value', 'BLUE')}")
            continue
        except ValueError:
            pass
        
        # Try textblock sources
        textblock, source_path = load_textblock(var, config, product_name, language)
        if textblock:
            resolved[var] = textblock
            # Show path relative to project root
            rel_path = source_path.relative_to(config.common_path.parent)
            print(f"  {colorize(var.ljust(20), 'YELLOW')} {colorize('←', 'BLUE')} {colorize(str(rel_path), 'CYAN')}")
            continue
            
        # Warn about unresolved variables
        print(f"  {colorize(var.ljust(20), 'RED')} {colorize('← WARNING: No source found', 'RED')}")
    
    return resolved

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
    """Build base context with core variables."""
    context = {
        "Config": config,
        "LANGUAGE": language.upper(),
        "PRODUCT": product_name,
        "CURRENCY": currency
    }
    
    # Colorized debug output
    print(colorize("\n⚙️ Template Context Setup", 'HEADER'))
    print(colorize(f"  Language:".ljust(15), 'BLUE') + colorize(language.upper(), 'CYAN'))
    print(colorize(f"  Product:".ljust(15), 'BLUE') + colorize(product_name, 'CYAN'))
    print(colorize(f"  Currency:".ljust(15), 'BLUE') + colorize(currency, 'CYAN'))
    print(colorize(f"  Output format:".ljust(15), 'BLUE') + colorize(config.settings.get('format', 'docx'), 'CYAN'))
    print()
    
    return context

def render_offer(template_path: Path, context: Dict[str, Any], output_path: Path):
    """Render template with auto-discovered variables"""
    if not template_path.exists():
        logger.error(f"Template file not found: {template_path}")
        sys.exit(1)

    try:
        doc = DocxTemplate(str(template_path))
        
        # Get all variables from the template
        template_vars = doc.get_undeclared_template_variables()
        print(f"\nDiscovering sources for {len(template_vars)} template variables:")
        
        # Resolve variables from multiple sources
        resolved_context = resolve_template_variables(template_vars, context['Config'], 
                                                   context['PRODUCT'], context['LANGUAGE'])
        
        # Merge with existing context
        context.update(resolved_context)

        # Render template with complete context
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
                
                # Get template path using template prefix
                template_path = Path(config.settings["templates"]) / f"base_{lang}.docx"
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
