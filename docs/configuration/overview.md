# Configuration System Overview

## Purpose
The configuration system provides a flexible and maintainable way to manage document generation settings, variables, and internationalization options. It uses YAML format for configuration files and supports template-based document generation with multi-language support.

## Structure
The configuration system is organized into several key components:

1. **Base Configuration**: Core settings for paths, internationalization, and output formats
2. **Product Configuration**: Product-specific settings and variables
3. **Variable System**: Support for dynamic content insertion with multi-language capabilities
4. **Template System**: Document templates with variable placeholders

## Key Features
- Hierarchical configuration structure
- Multi-language support
- Flexible path configuration
- Template-based document generation
- Variable substitution system

## Environment Variables

The following environment variables can be used to customize the behavior of ODG:

- **TEST_OUTPUT_DIR**: Specifies the directory where test files (e.g., templates, sample documents) will be generated. This is particularly useful during testing to ensure output is isolated.

Example usage:
```bash
export TEST_OUTPUT_DIR=/path/to/test/dir
odg create-template --name=test_template.docx
```

For detailed information about specific aspects of the configuration system, please refer to:
- [Folder Structure](folder_structure.md)
- [Variables Documentation](variables.md)
- [Internationalization](internationalization.md)
