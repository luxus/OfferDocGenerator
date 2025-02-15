import sys
import logging
import traceback
import json
from datetime import datetime
import os

logger = logging.getLogger(__name__)
security_logger = logging.getLogger('security')

def log_security_event(event_type: str, details: dict):
    """Log security-related events with context"""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "user": os.getlogin(),
        "event": event_type,
        "details": details
    }
    security_logger.warning(json.dumps(log_entry))

class DocumentGenerationError(Exception):
    """Base exception for document generation errors"""
    pass

class SecurityError(DocumentGenerationError):
    """Base class for security-related exceptions"""
    pass

class PathTraversalError(SecurityError):
    """Raised when path traversal attempt detected"""
    pass

class UnsafeContentError(SecurityError):
    """Raised when dangerous content is detected"""
    pass

class TemplateNotFoundError(DocumentGenerationError):
    """Raised when a template file is missing"""
    pass

class InvalidConfigError(DocumentGenerationError):
    """Raised for configuration validation errors"""
    pass

def handle_document_errors(func):
    """Decorator for handling document generation errors"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except DocumentGenerationError as e:
            logger.error(f"Document generation failed: {str(e)}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Unexpected error: {traceback.format_exc()}")
            sys.exit(2)
    return wrapper
