from pathlib import Path
from typing import List
import logging
from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from src.config.settings import Config

logger = logging.getLogger(__name__)

class FileHandler:
    def __init__(self, config: Config):
        self.config = config

    def find_templates(self, language: str = None) -> List[Path]:
        """Find all template files in the templates directory."""
        pattern = f"*_{language}.docx" if language else "*.docx"
        templates = list(self.config.templates_path.glob(pattern))
        logger.info(f"Found {len(templates)} templates matching pattern {pattern}")
        return templates

    def get_common_fragments(self, language: str = None) -> List[Path]:
        """Get common DOCX fragments from the common directory."""
        pattern = f"*_{language}.docx" if language else "*.docx"
        fragments = list(self.config.common_path.glob(pattern))
        logger.info(f"Found {len(fragments)} common fragments matching pattern {pattern}")
        return fragments

    def save_output(self, content: bytes, filename: str) -> Path:
        """Save generated document to output directory."""
        output_path = self.config.output_path / filename
        output_path.parent.mkdir(exist_ok=True, parents=True)
        
        logger.info(f"Saving document to {output_path}")
        with open(output_path, "wb") as f:
            f.write(content)
            
        return output_path

    def has_numbered_lists(self, docx_path: Path) -> bool:
        """Check if DOCX file contains numbered lists"""
        try:
            document = Document(str(docx_path))
            
            # Check both style name and numbering property
            for paragraph in document.paragraphs:
                if (paragraph.style and 
                    (paragraph.style.name.startswith("List Number") or
                     hasattr(paragraph, "_element") and 
                     paragraph._element.pPr and 
                     paragraph._element.pPr.numPr is not None)):
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Error checking numbered lists: {e}")
            return False

    def validate_doc_structure(self, docx_path: Path) -> bool:
        """Verify basic DOCX structure requirements"""
        document = Document(str(docx_path))
        
        # Basic checks
        assert len(document.sections) >= 1, "No sections found"
        assert any(p.text.strip() for p in document.paragraphs), "Empty document"
        
        return True

    def has_required_sections(self, docx_path: Path, is_product: bool = False) -> bool:
        """Verify presence of required sections"""
        try:
            document = Document(str(docx_path))
            
            required_sections = [
                "Introduction",
                "Product Overview" if is_product else "General Information", 
                "Technical Specifications"
            ]
            
            # Get all heading level 1 paragraphs
            headings = [
                p.text.strip() 
                for p in document.paragraphs 
                if p.style and p.style.name.startswith("Heading 1")
            ]
            
            # Check if all required sections are present
            missing_sections = [
                section for section in required_sections 
                if not any(heading.startswith(section) for heading in headings)
            ]
            
            if missing_sections:
                logger.warning(f"Missing required sections: {missing_sections}")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error checking required sections: {e}")
            return False
