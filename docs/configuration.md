# Configuration Options

The application uses a YAML-based configuration system with several key sections.

## Base Configuration

All configurations inherit from `BaseConfig` which provides core validation logic.

### Required Fields:
- `app_name`: Name of your application (string)
- `output_path`: Root directory for generated documents (Path)
- `template_path`: Directory containing template files (Path)

### Optional Fields:
- `default_language`: Default language code (e.g. "en") 
- `currency_format`: Currency formatting rules
- `logging_config`: Logging configuration options

## AppConfig Extension

The `AppConfig` class extends BaseConfig with additional application-specific settings.

### Additional Fields:
- `supported_languages`: List of supported language codes
- `template_variables`: Dictionary mapping variable names to their definitions
- `security_restrictions`: Path restrictions for file operations
