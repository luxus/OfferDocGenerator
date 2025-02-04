from pathlib import Path
from typing import Dict, Any, Set
from docxtpl import DocxTemplate
from .file_handler import FileHandler
from .config import AppConfig
from .exceptions import TemplateNotFoundError, DocumentGenerationError
import logging

logger = logging.getLogger(__name__)

class DocumentRenderer:
    """Handles template rendering with dependency injection"""
    
    def __init__(self, file_handler: FileHandler, config: AppConfig):
        self.file_handler = file_handler
        self.config = config

    def resolve_variables(self, template: DocxTemplate, product: str, 
                         language: str) -> Dict[str, Any]:
        """Resolve template variables using config and textblocks"""
        template_vars = template.get_undeclared_template_variables()
        return self._resolve_template_variables(template_vars, product, language, template)

    def _resolve_template_variables(self, template_vars: Set[str], product: str,
                                  language: str, template: DocxTemplate) -> Dict[str, Any]:
        """Internal method to resolve variables from multiple sources"""
        resolved = {}
        
        for var in sorted(template_vars):
            # Try config resolution first
            try:
                resolved[var] = self._resolve_config_variable(var)
                continue
            except (ValueError, AttributeError):
                pass
                
            # Try textblock resolution
            subdoc, _ = self.file_handler.load_textblock(var, product, language, template)
            if subdoc:
                resolved[var] = subdoc
                continue
                
            # Fallback to empty string
            resolved[var] = ""
            logger.warning(f"No value found for template variable: {var}")
            
        return resolved

    def _resolve_config_variable(self, var_path: str) -> Any:
        """Resolve dot-notation variable paths in config"""
        path_parts = var_path.split('_')
        current = self.config
        
        for part in path_parts:
            if hasattr(current, part):
                current = getattr(current, part)
            else:
                raise ValueError(f"Config path not found: {var_path}")
            
        return current

    def render_document(self, template_path: Path, context: Dict[str, Any]) -> DocxTemplate:
        """Main rendering operation"""
        if not template_path.exists():
            raise TemplateNotFoundError(f"Template not found: {template_path}")

        try:
            doc = DocxTemplate(str(template_path))
            
            # Update context with resolved variables
            template_vars = doc.get_undeclared_template_variables()
            resolved = self.resolve_variables(doc, context['PRODUCT'], context['LANGUAGE'])
            context.update(resolved)
            
            # Render with complete context
            doc.render(context, autoescape=True)
            return doc
            
        except Exception as e:
            raise DocumentGenerationError(f"Rendering failed: {str(e)}") from e
