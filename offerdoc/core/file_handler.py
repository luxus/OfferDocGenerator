from pathlib import Path
from typing import Optional, Tuple, Union
from docxtpl import DocxTemplate, RichText
from .exceptions import SecurityError
from docxcompose.composer import Composer
from .config import AppConfig
from .exceptions import TemplateNotFoundError
import logging

logger = logging.getLogger(__name__)

class FileHandler:
    """Handles all file system operations with config-aware paths"""
    
    def __init__(self, config: AppConfig):
        self.config = config
        
    def _validate_file_security(self, path: Path) -> None:
        """Enforce security settings from config"""
        settings = self.config.settings.security
        
        # Size check
        file_size = path.stat().st_size
        if file_size > settings.max_template_size_mb * 1024 * 1024:
            raise SecurityError(f"File {path.name} exceeds size limit")
        
        # Type check
        if path.suffix[1:] not in settings.allowed_file_types:
            raise SecurityError(f"Disallowed file type: {path.suffix}")
        
        # Ownership check
        if path.owner() != Path(__file__).owner():
            raise SecurityError("File owner mismatch")
            
    def find_textblock(self, var_name: str, product: str, language: str, bundle: Optional[str] = None) -> Optional[Path]:
        """Search for textblocks using configured patterns"""
        search_locations = [
            self.config.products_path / product,
            self.config.common_path
        ]
        
        if bundle:
            search_locations.insert(0, self.config.common_path / "bundles" / bundle)

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
                      template: DocxTemplate) -> Tuple[Optional[str], Optional[Path]]:
        """Load textblock content as plain text"""
        MAX_TEXTBLOCK_LENGTH = 10000  # 10k characters limit
        target_path = self.find_textblock(var_name, product, language)
        if target_path:
            try:
                self._validate_file_security(target_path)
                subdoc = DocxTemplate(str(target_path))
                text = '\n'.join(p.text for p in subdoc.paragraphs if p.text.strip())
                
                if len(text) > MAX_TEXTBLOCK_LENGTH:
                    raise ValueError(f"Textblock {target_path} exceeds size limit")
                
                # Prevent nested templates
                if '{{' in text or '{%' in text:
                    raise ValueError("Nested template patterns detected")
                    
                return text, target_path
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
