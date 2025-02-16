# ODG - Offer Document Generator

A command-line tool for generating offer documents with multi-language support.

## Features

- Multi-language document generation
- Template-based document creation with Jinja2 support
- YAML configuration
- Flexible folder structure
- Enhanced section validation

## Installation

```bash
pip install odg
```

## Usage

```bash
# Create a new project structure
odg create my_project

# Show version
odg --version
```

## Environment Variables

- **TEST_OUTPUT_DIR**: Optional directory for test file generation (e.g., when running pytest). Useful to isolate output files during testing.

Example usage in tests:
```bash
export TEST_OUTPUT_DIR=/path/to/test/dir
pytest
```

## License

MIT License
