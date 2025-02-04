class DocumentGenerationError(Exception):
    """Base exception for document generation errors"""
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
