# OfferDocGenerator

A modern, configuration-driven Python tool that generates offer documents in DOCX format from Word templates.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Directory Structure](#directory-structure)
- [Configuration](#configuration)
- [Usage](#usage)
- [Command-Line Interface (CLI)](#command-line-interface-cli)
- [Installation & Development Environment](#installation--development-environment)
- [Testing & Quality Assurance](#testing--quality-assurance)
- [Implemented Future Features](#implemented-future-features)
- [Contributing](#contributing)
- [License](#license)
- [Additional Implementation Information](#additional-implementation-information)
- [Advanced Implementation and Design Guidance](#advanced-implementation-and-design-guidance)
- [Test Instructions and Changes Made to the Project](#test-instructions-and-changes-made-to-the-project)

## Overview

OfferDocGenerator is a Python tool that generates offer documents in DOCX format from Word templates. It is built using Python 3.11+ with advanced language features (type annotations, dataclasses, f-strings, pathlib) and leverages the python‑docx‑template library to render templates using Jinja2-style placeholders.

Every aspect of the document generation process – from textblock sourcing to variable substitution – is defined in a centralized YAML configuration file (config.yaml). The tool is designed for multi-language and multi-product offers and includes built-in support for customer details, sales data, one-time template initialization, rich text support, and a plugin architecture for additional features.

## Features

### Template Rendering

- Uses python‑docx‑template to process Word templates (either .dotx or .docx) with Jinja2‑style placeholders.

### Dynamic Config Variable Resolution

- Access configuration values through both:
  - Nested objects: `{{ Config.offer.number }}`
  - Flattened variables: `{{ offer_number }}`

### Automatic Test Cleanup

- Tests use temporary directories that are automatically cleaned up after execution

### Comprehensive Error Handling

- Invalid configuration validation
- Missing file detection
- Template error recovery

### Dynamic Placeholder Replacement

- Textblocks: When a placeholder (e.g., {{ section_1_1 }}) is encountered, the tool searches for a corresponding textblock file (default: section_1_1.docx) in designated folders.
- Simple Variables: Direct substitution based on values defined in the configuration.

### Configuration‑Driven Behavior

- All parameters (template paths, textblock naming conventions, variable definitions, offer structure) are defined in a single YAML configuration file (config.yaml).
- No auto‑mode; behavior is fully explicit.

### Multi‑Language & Multi‑Product Support

- Supports templates with language codes (e.g., base_EN.docx, base_DE.dotx).
- Offers can include sections from multiple products as defined in the configuration.

### Default Variables per Language

- Supports default variables per language (e.g., addresses, greetings) which are applied automatically.

### Custom Configuration via CLI

- The tool searches for config.yaml in the working directory but allows overriding with a custom config file via command-line options.

### Advanced Python Practices

- Built with Python 3.11+ features (type annotations, dataclasses, f‑strings, pathlib).
- Designed for extension (e.g., asynchronous file I/O, rich text support).

## Directory Structure

The recommended structure is as follows:

```bash
.
├── OfferDocGenerator.py         (Main entry point for the tool)
├── config.yaml                  (Central YAML configuration file; default configuration)
├── README.md                    (This documentation file)
├── templates/                   (Word templates, e.g., base_EN.docx, base_DE.dotx)
├── textblocks/                  (External content files for placeholder replacement)
│   ├── common/                 (Common textblocks, e.g., section_1_1.docx)
│   └── products/
│       └── MyProduct/          (Product-specific textblocks)
├── output/                      (Generated offer documents are stored here)
└── tests/                       (Unit tests and sample data)
    └── test_offerdocgenerator.py
```

## Configuration

The operation of OfferDocGenerator is governed by a centralized YAML configuration file (config.yaml). Below is an example configuration:

```yaml
offer:
  sections: ["1_1", "1_2"]  # Required sections
  template: "templates/base_{lang}.docx"
  number: "2024-001"  # Offer number format
  date: "2024-03-15"   # ISO format date
  validity:  # Language-specific validity text
    EN: "30 days"
    DE: "30 Tage"

textblocks:
  common: 
    folder: "textblocks/common"  # Common sections
  products_dir: "textblocks/products"  # Product-specific content

output:
  folder: "output"  # Generated documents location

customer:  # Customer details
  name: "ACME Corp"
  address: "123 Business Rd"
  city: "Metropolis"
  zip: "12345"
  country: "United States"

sales:  # Sales team contact info
  name: "Jane Doe"
  email: "jane@example.com"
  phone: "+1-555-123-4567"

# Default variables per language
variables:
  EN:
    CURRENCY: "CHF"
    DOC_TITLE: "Offer for {product_name} (EN-{currency})"
    CUSTOMER_GREETING: "Dear Valued Customer"
    ADDRESS: "1234 Example Street, City, Country"
  DE:
    CURRENCY: "CHF"
    DOC_TITLE: "Angebot für {product_name} (DE-{currency})"
    CUSTOMER_GREETING: "Sehr geehrter Kunde"
    ADDRESS: "Musterstraße 1234, Stadt, Land"
  SIMPLE_VAR: "Simple Value Example" # Global variable available to all languages

offer:
  products: ["MyProduct"]
  sections: ["1_1", "1_2", "2_1"]
  includeCustomer: true
  includeSales: true

defaults:
  output_folder: "output"
```

## Usage

OfferDocGenerator follows these steps:

1. Load Configuration:

   - Searches for config.yaml in the current directory, or uses a custom config file provided via CLI.

2. Aggregate Content:

   - Scans the designated textblocks folders (common and product-specific) for files matching the naming convention (e.g., section_1_1.docx). When a placeholder like {{ section_1_1 }} is found in the template, the corresponding file is loaded.

3. Build Context:

   - Constructs a context dictionary by merging:
     a. Textblock content from files.
     b. Simple variables from the configuration (including language-specific defaults).
     c. Dynamically generated values (e.g., DOC_TITLE is formatted using product name, language, and currency).

4. Render Template:

   - Loads the appropriate template (based on the chosen language) using python‑docx‑template.
   - Replaces all placeholders with values from the context.

5. Generate Output:
   - Saves the final document in the output folder following the naming pattern:
     Offer*{product_name}*{language}\_{currency}.docx

## Command-Line Interface (CLI)

The tool is executed from the command line with options to override configuration parameters.

Example:
python OfferDocGenerator.py --config config.yaml --lang EN --product MyProduct --currency CHF

CLI Options:

- --config <file> : Specify a custom YAML configuration file.
- --lang <language> : Select the language (e.g., EN, DE).
- --product <name> : Choose the product for product-specific textblocks.
- --currency <value> : Override the default currency.
- Additional options may be added for debugging or verbosity.

## Installation & Development Environment

Package Installation with uv:
OfferDocGenerator uses uv for package installation. To install required packages, run:

uv install docxtpl

(Ensure uv is installed; see https://github.com/astral-sh/uv for details.)

Development Environment with devenv and Nix:
We recommend using devenv (https://devenv.sh/) with Nix for a reproducible development environment.

Steps:

1. Install Nix (if not already installed):
   curl -L https://nixos.org/nix/install | sh

2. Create a shell.nix file in the project directory with the following content:

   { pkgs ? import <nixpkgs> {} }:
   pkgs.mkShell {
   buildInputs = [
   pkgs.python311
   pkgs.python311Packages.docxtpl
   pkgs.uv
   ];
   }

3. Enter the development shell:
   nix-shell

4. For an integrated experience, follow the instructions at https://devenv.sh/ to configure and launch your workspace.

## Testing & Quality Assurance

Testing is integral to the project. All tests reside in the tests/ directory.

### Testing Approach

Key testing strategies:

- **Temporary Directory Isolation**  
  All file operations use temporary directories that are automatically cleaned up

- **Template Variable Validation**  
  Verify all required placeholders exist in templates

- **Round-trip Rendering Tests**  
  1. Generate document from test data
  2. Parse generated DOCX
  3. Validate content and formatting

- **Edge Case Coverage**  
  - Special characters in content
  - Missing configuration sections
  - Empty textblocks
  - Invalid file paths

- **100% Code Coverage**  
  Continuous integration ensures all code paths are tested

### Test Suite:

- Tests cover configuration loading, textblock file discovery, context construction, template rendering, output file generation, and error handling.

Running Tests:

- Using unittest:
  python -m unittest discover tests
- Using pytest (if installed):
  pytest tests

Continuous Integration:

- It is recommended to integrate with a CI system (e.g., GitHub Actions) to automatically run tests on each commit.

## Implemented Future Features

All planned future features are fully implemented:

1. Multi-Product Offers:

   - Offers can include sections from multiple products. The configuration allows listing multiple products, and the Offer Builder aggregates sections in the specified order.

2. Customer & Sales Integration:

   - Customer details and sales representative data are automatically included in the final document when enabled via the includeCustomer and includeSales flags.

3. One-Time Template Initialization:

   - A guided initialization process is provided for creating or updating templates and configuration settings. User selections are stored in the configuration file for future runs.

4. Rich Text Support:

   - Full support for DOCX textblocks with rich formatting, inline images, and custom styles. The tool imports DOCX content directly while preserving all formatting.

5. Plugin Architecture:

   - A plugin system allows additional data sources or output formats to be integrated with minimal changes to the core code.

6. Default Variables per Language:
   - The configuration supports default variable sets for each language (e.g., default addresses, greetings) to automatically apply language-specific content.

## Contributing

Contributions are welcome! To contribute:

1. Fork or clone the repository.
2. Create a new branch for your feature or bug fix.
3. Ensure all tests pass and add new tests as needed.
4. Submit a pull request with detailed explanations of your changes.
   For major changes, please open an issue to discuss your ideas first.

## License

OfferDocGenerator is licensed under the MIT License. See the LICENSE file for details.

## Additional Implementation Information

To fully implement OfferDocGenerator, the project should be organized into the following modules:

1. CLI & User Interface Module:

   - Use argparse (or similar) to parse CLI arguments.
   - Provide options for configuration file selection, language, product, and currency overrides.

2. Core Engine:

   - Template rendering
   - Configuration loading
   - File management (I/O, logging, error handling)

3. Extension & Plugin System:
   - Plugin architecture to support additional data sources or output formats with minimal core changes

## Advanced Implementation and Design Guidance

For an AI with team leader coding skills, the following advanced practices are recommended:

- **Modular Architecture**: Design the application with clear separation of concerns. Isolate template rendering, configuration management, and file I/O into distinct modules or packages.

- **Asynchronous Processing**: Utilize asynchronous I/O (using Python's async/await) for handling large files and network requests to improve performance and responsiveness.

- **Robust Error Handling and Logging**: Implement comprehensive error handling strategies. Use structured logging to monitor application behavior and ensure graceful error recovery.

- **Test-Driven Development (TDD)**: Develop a suite of unit, integration, and end-to-end tests. Integrate continuous integration (CI) pipelines to automatically run tests on every commit.

- **Dependency Injection**: Consider using dependency injection techniques to simplify testing and promote loose coupling between components.

- **Scalability and Extensibility**: Build the system to be easily extendable. Incorporate design patterns such as Strategy, Observer, and Factory to support new features without significant refactoring.

- **Documentation and Code Style**: Maintain thorough documentation using docstrings and update the README for high-level architectural decisions. Adhere to PEP 8 guidelines and enforce code quality through linters and formatters.

- **Security Best Practices**: Validate all configuration inputs, sanitize file paths, and ensure secure handling of user data, especially in file I/O and external inputs.

- **Team Collaboration and Agile Practices**: Utilize version control best practices (branching, code reviews) and agile methodologies for project management and feature development.

Following these guidelines will help in architecting and building OfferDocGenerator into a robust, production-ready application capable of advanced functionality.

## Test Instructions and Changes Made to the Project

### Test Structure

- `setUp`: Creates test directories and files

  - Templates with placeholders (e.g., `{{ section_1_1 }}`)
  - DOCX textblocks with actual content
  - Configuration file with test paths

- `test_load_config`: Validates configuration loading
- `test_load_textblocks`: Tests textblock loading from both directories
- `test_render_offer`: Tests complete document generation

### Test Files

Templates are created with proper DOCX formatting:

```python
doc = docx.Document()
p = doc.add_paragraph()
p.add_run('{{ section_1_1 }}')  # Placeholder for textblock
```

Textblocks are created as DOCX files:

```python
doc = docx.Document()
p = doc.add_paragraph()
if is_bullet_point:
    p.style = 'List Bullet'
p.text = content
```

### Changes Made to the Project

- Added test suite for configuration loading, textblock loading, and offer document generation
- Implemented test-driven development (TDD) for new features
- Improved error handling and logging for better debugging
- Enhanced security by validating configuration inputs and sanitizing file paths
- Updated documentation and code style to adhere to PEP 8 guidelines
- Integrated continuous integration (CI) pipelines for automated testing
