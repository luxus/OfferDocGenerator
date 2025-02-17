# Offer Document Generator (ODG)

A command-line tool for generating and managing offer documents with multi-language support and configurable templates.

## Key Features
- Template-based document generation with Jinja2 support
- Multi-language support (en, de, fr)
- Configurable project structure
- Built-in configuration validation
- Security-aware file handling
- Automated document merging capabilities
- Proper numbered list handling with consistent formatting
- Multi-level list support with correct indentation

## Quick Start

Install the package:
```bash
pip install odg
```

Create a new project:
```bash
odg create --output-dir my_project
```

This creates a directory structure with:
```
my_project/
├── templates/     # Document templates
├── common/        # Shared document fragments
├── products/      # Product-specific templates
├── output/        # Generated documents
└── generated/     # Temporary files
```

## Configuration

The generated `config.yaml` must include these sections:

```yaml
settings:
  base_path: "/path/to/project"
  output_prefix: "DOC-"
  folders:
    templates: "templates"
    common: "common"
    products: "products"
    output: "output"
    generated: "generated"

offer:
  number: "OFR-{{date}}-{{number}}"
  date: "{{current_date}}"
  validity: "30 days"
  currency: "{{currency}}"
  language: "{{language}}"

customer:
  details:
    name: "{{customer_name}}"
    address: "{{customer_address}}"

sales:
  representative: "{{sales_rep}}"
  email: "{{sales_email}}"

internationalization:
  default_language: "en"
  supported_languages: ["en", "de", "fr"]
```

## Document Formatting

Documents are generated with consistent formatting:
- First-level numbered lists: 0.5 inch left indent
- Second-level numbered lists: 1.0 inch left indent
- Default font size: 14pt
- Automatic numbering continuation across merged documents

## Usage Examples

1. Generate documents:
```bash
odg generate --product "Product Name" --language en --currency EUR
```

2. Validate configuration:
```bash
odg validate --directory <project_directory>
```

3. Create a sample document:
```bash
odg create-sample --product "Product Name" --language en --currency EUR
```

## Commands

Check version:
```bash
odg --version
```

Create new project:
```bash
odg create <output_directory>
```

For detailed configuration options, see the configuration guide.

## Development

Requirements:
- Python 3.12+
- python-docx
- Jinja2
- pydantic
- PyYAML

For development setup:
1. Clone the repository
2. Install dependencies: `pip install -r requirements-dev.txt`
3. Run tests: `pytest tests/`
