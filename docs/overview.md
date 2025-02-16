# Offer Document Generator (ODG)

A command-line tool for generating and managing offer documents with multi-language support and configurable templates.

## Key Features
- Template-based document generation
- Multi-language support (en, de, fr)
- Configurable project structure
- Built-in configuration validation
- Security-aware file handling

## Quick Start

Install the package:
```bash
pip install odg
```

Create a new project:
```bash
odg create my_project
```

This creates a directory structure with:
- templates/
- common/
- products/
- output/
- config.yaml

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
