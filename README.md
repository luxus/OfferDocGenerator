# ODG - Offer Document Generator

A command-line tool for generating offer documents with multi-language support.

## Features

- Multi-language document generation (en, de, fr)
- Template-based document creation with Jinja2 support
- YAML configuration with validation
- Flexible folder structure
- Enhanced section validation
- Proper numbered list handling
- Consistent document formatting
- Automated document merging

## Installation

```bash
pip install odg
```

## Quick Usage

```bash
# Create a new project structure
odg create my_project

# Generate a document
odg generate --product "Product Name" --language en --currency EUR

# Validate configuration
odg validate --directory my_project

# Show version
odg --version
```

## Configuration

Required configuration sections:
- settings
- offer
- customer
- sales
- internationalization

See `docs/overview.md` for detailed configuration options.

## Document Features

- Multi-level numbered lists
- Consistent formatting
- Template variables
- Merged document support
- Multiple language support

## Development

Requirements:
- Python 3.12+
- python-docx
- Jinja2
- pydantic
- PyYAML

## Testing

```bash
pytest tests/
```

## License

MIT

## Contributing

See CONTRIBUTING.md for guidelines.
