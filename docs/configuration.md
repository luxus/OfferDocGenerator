# Configuration Options

The application uses a YAML-based configuration system with several key sections.

## Base Configuration

All configurations inherit from `BaseConfig` which provides core validation logic. The settings section defines folder locations and output preferences.

### Required Fields:
- `app_name`: Name of your application
- `output_path`: Root directory for generated documents
- `base_path`: Base directory for all relative paths

### Optional Fields:
- `default_language`: Default language code (e.g. "en")
- `currency_format`: Currency formatting rules
- `logging_config`: Logging configuration options

## AppConfig Extension

The `AppConfig` class extends BaseConfig with additional application-specific settings and folder configurations.

### Additional Fields:
- `supported_languages`: List of supported language codes
- `template_variables`: Dictionary mapping variable names to their definitions
- `security_restrictions`: Path restrictions for file operations

### Folder Configuration:
The configuration can specify folder locations through the `folders` dictionary:

```yaml
settings:
  folders:
    templates: "./templates"
    common: "./common"
    products: "./products"
    output: "./output"
  output_prefix: "DOC-"
```
