from pathlib import Path
import re
import magic
from typing import List

def sanitize_filename(name: str) -> str:
    """Sanitize filenames to prevent path traversal"""
    cleaned = re.sub(r'[^a-zA-Z0-9_\-.]', '', name)
    return cleaned[:255]  # Limit filename length

def validate_file_type(file_path: Path, allowed_types: List[str]) -> bool:
    """Validate file type using magic numbers"""
    mime = magic.Magic(mime=True)
    detected_type = mime.from_file(str(file_path))
    return detected_type in allowed_types

def safe_template_rendering(template_path: Path, max_size_mb: int = 10) -> None:
    """Security checks before template rendering"""
    max_size = max_size_mb * 1024 * 1024
    if template_path.stat().st_size > max_size:
        raise ValueError(f"Template exceeds size limit: {template_path}")
    
    allowed_types = ['application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    if not validate_file_type(template_path, allowed_types):
        raise ValueError(f"Invalid file type: {template_path}")
