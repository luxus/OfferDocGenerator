# ODG - Offer Document Generator

A command-line tool for generating offer documents with multi-language support.

## Features

- Multi-language document generation
- Template-based document creation
- YAML configuration
- Flexible folder structure

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

- **TEST_OUTPUT_DIR**: Optional directory for test file generation. Useful during testing to isolate output files.

Example:
```bash
export TEST_OUTPUT_DIR=/path/to/test/dir
odg create-template --name=test_template.docx
```

## License

MIT License
