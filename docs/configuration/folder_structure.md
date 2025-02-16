# Project Folder Structure

## Overview
The project uses a structured folder layout to organize templates, configurations, and resources:

```
project/
├── base/                 # Base files (templates, common assets)
├── templates/            # Docx template files
├── products/            # Product-specific configuration and data
│   ├── product1/
│   │   ├── config.yaml
│   │   └── data/
│   └── product2/
├── common/              # Shared resources (images, styles)
└── output/              # Generated documents
```

## Default Paths
The following paths are used by default but can be customized in the configuration:

- `base_path`: `./base`
  - Contains base templates and common resources
  - Used as the foundation for all document generation

- `templates_path`: `./templates`
  - Stores all document templates
  - Templates use the .docx format with variable placeholders

- `products_path`: `./products`
  - Product-specific configurations
  - Each product has its own subfolder with config.yaml

- `common_path`: `./common`
  - Shared resources like images and styles
  - Used across multiple products and templates

- `output_path`: `./output`
  - Destination for generated documents
  - Follows the configured naming scheme

## Customization
Paths can be customized in the main configuration file:

```yaml
paths:
  base: ./custom/base
  templates: ./custom/templates
  products: ./custom/products
  common: ./custom/shared
  output: ./custom/output
```
