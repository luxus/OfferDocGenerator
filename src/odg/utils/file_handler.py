import logging
from pathlib import Path
from typing import List
from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from src.config.settings import Config

logger = logging.getLogger(__name__)

class FileHandler:
    def __init__(self, config: Config):
        self.config = config
        self.output_dir = Path(config.output_dir)

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
        output_path = self.output_dir / "output" / filename
        output_path.parent.mkdir(exist_ok=True, parents=True)
        
        logger.info(f"Saving document to {output_path}")
        with open(output_path, "wb") as f:
            f.write(content)
            
        return output_path

    def has_numbered_lists(self, docx_path: Path) -> bool:
        """Check if DOCX file contains numbered lists."""
        try:
            document = Document(str(docx_path))
            return any(p.style.name.startswith('List Number') 
                      for p in document.paragraphs)
        except Exception as e:
            logger.error(f"Error checking numbered lists: {e}")
            return False

    def validate_doc_structure(self, docx_path: Path) -> bool:
        """Verify basic DOCX structure requirements"""
        try:
            document = Document(str(docx_path))
            return any(p.style.name.startswith("Heading") 
                      for p in document.paragraphs)
        except Exception as e:
            logger.error(f"Structure validation error: {e}")
            return False

    def validate_merged_doc(self, docx_path: Path) -> bool:
        """Check if the merged document has valid structure."""
        try:
            document = Document(str(docx_path))
            
            # Track section numbering
            current_section = 0
            sub_section_count = 0
            
            for paragraph in document.paragraphs:
                if paragraph.style.name.startswith("Heading"):
                    level = int(paragraph.style.name.split()[-1])
                    
                    text = paragraph.text.strip()
                    if not text:
                        continue
                    
                    # Allow both numbered and unnumbered sections
                    if level == 1:
                        current_section += 1
                        sub_section_count = 0
                    elif level == 2:
                        sub_section_count += 1
            
            return True
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False

    def has_required_sections(self, docx_path: Path) -> bool:
        """Verify presence of required sections."""
        try:
            document = Document(str(docx_path))
            headings = [p.text.strip() for p in document.paragraphs 
                       if p.style.name.startswith("Heading")]
            
            required_sections = ["Introduction", "Product Overview", "Technical Specifications"]
            return all(any(section in h for h in headings) 
                      for section in required_sections)
        except Exception as e:
            logger.error(f"Error checking sections: {e}")
            return False
