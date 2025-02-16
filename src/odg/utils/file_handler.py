import os
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
        # Ensure the file is saved within the output_dir's output subdirectory
        output_path = self.output_dir / "output" / filename
        output_path.parent.mkdir(exist_ok=True, parents=True)
        
        logger.info(f"Saving document to {output_path}")
        with open(output_path, "wb") as f:
            f.write(content)
            
        return output_path

    def has_numbered_lists(self, docx_path: Path) -> bool:
        """Check if DOCX file contains numbered lists with nesting."""
        try:
            document = Document(str(docx_path))
            
            number_style_found = False
            nested_number_style_found = False
            
            for paragraph in document.paragraphs:
                style_name = getattr(paragraph.style, 'name', '')
                if style_name and 'List Number' in style_name:
                    if 'List Number 2' in style_name:
                        nested_number_style_found = True
                    else:
                        number_style_found = True
                
                if number_style_found and nested_number_style_found:
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

    def validate_merged_doc(self, docx_path: Path) -> bool:
        """Check if the merged document has continuous section numbering."""
        try:
            document = Document(str(docx_path))
            
            current_section_number = 0
            for paragraph in document.paragraphs:
                if paragraph.style.name.startswith("Heading"):
                    level = int(paragraph.style.name.split()[-1])
                    text_parts = paragraph.text.split('.')
                    if len(text_parts) >= 2 and text_parts[0].isdigit():
                        section_num = int(text_parts[0])
                        if section_num != current_section_number + 1:
                            logger.warning(f"Section numbering discontinuity at {paragraph.text}")
                            return False
                        current_section_number += 1
            
            return True
        
        except Exception as e:
            logger.error(f"Error validating merged document: {e}")
            return False

    def has_required_sections(self, docx_path: Path, is_product: bool = False) -> bool:
        """Verify presence of required sections"""
        try:
            document = Document(str(docx_path))
            
            # Define base required sections
            required_sections = ["Introduction", "Technical Specifications"]
            
            # Add specific sections based on document type
            if is_product:
                required_sections.append("Product Overview")
            else:
                required_sections.append("General Information")
            
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
