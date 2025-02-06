from pathlib import Path
from typing import Optional, Tuple, Union
from docxtpl import DocxTemplate, RichText
from docxcompose.composer import Composer
from .config import AppConfig
from .exceptions import TemplateNotFoundError
import logging

logger = logging.getLogger(__name__)

class FileHandler:
    """Handles all file system operations with config-aware paths"""
    
    def __init__(self, config: AppConfig):
        self.config = config
        
    def find_textblock(self, var_name: str, product: str, language: str) -> Optional[Path]:
        """Search for textblocks using configured patterns"""
        search_locations = [
            self.config.products_path / product,
            self.config.common_path
        ]

        for base_path in search_locations:
            for pattern in self.config.textblock_patterns:
                target_path = base_path / pattern.format(
                    var_name=var_name,
                    language=language.upper()
                )
                if target_path.exists():
                    return target_path
        return None

    def load_textblock(self, var_name: str, product: str, language: str, 
                      template: DocxTemplate) -> Tuple[Optional[Union[RichText, DocxTemplate]], Optional[Path]]:
        """Load textblock content for inline insertion"""
        target_path = self.find_textblock(var_name, product, language)
        if target_path:
            try:
                subdoc = DocxTemplate(str(target_path))
                rt = RichText()
                
                # Preserve original paragraph structure but merge into single line
                for i, p in enumerate(subdoc.paragraphs):
                    if p.text.strip():  # Skip empty paragraphs
                        # Use the template's style for continuity
                        rt.add(p.text + " ", style='List Paragraph')  # Add space between paragraphs
                        
                # Remove trailing space and add continuation character
                if rt.text.endswith(" "):
                    rt.text = rt.text[:-1]
                
                return rt, target_path
            except Exception as e:
                logger.error(f"Failed to load subdoc {target_path}: {e}")
                raise
        return None, None

    def ensure_output_dir(self, product: str) -> Path:
        """Create output directory if needed"""
        output_dir = self.config.output_path / product
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    def get_template_path(self, language: str) -> Path:
        """Get template path for given language"""
        template_filename = self.config.settings.template_pattern.format(language=language)
        return self.config.templates_path / template_filename

    def get_output_path(self, product: str, language: str, currency: str, date: str) -> Path:
        """Generate output file path based on config pattern"""
        output_dir = self.ensure_output_dir(product)
        filename = self.config.settings.filename_pattern.format(
            product=product,
            language=language,
            currency=currency,
            date=date,
            format=self.config.settings.format
        )
        return output_dir / filename
