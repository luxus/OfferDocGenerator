# Default Folder Structure

The default folder structure assumes a root directory where all configuration and assets are stored. This can be overwritten in the main configuration file.

```
base/
├── templates/                # Main template files (e.g., main_de.docx, section1_1_en.docx)
│   ├── common/              # Common template fragments used across sections/languages
│   └── Web Application Security Assessment/   # Product-specific template folder
│       └── section1_1_de.docx   # Example template file with language suffix
├── products/                # Product-specific configuration and data
│   ├── product1/            # Example product folder
│   │   ├── config.yaml     # Product-specific configuration (optional)
│   │   └── data/           # Additional product-related files (e.g., images, custom templates)
│   └── product2/            # Another product example
├── common/                  # Shared DOCX fragments and assets used across all products
└── output/                  # Generated documents
```

## Explanation of Folders

### `templates/`
- Contains the main template files.
- Templates use language suffixes in filenames (e.g., `_de.docx`, `_en.docx`).
- Product-specific templates are stored in their own subfolders under `templates/`.

### `common/`
- Shared resources used across all products and sections.
- Includes:
  - Images and media files
  - Style definitions
  - Common DOCX fragments

### `products/`
- Folder for product-specific configurations and data.
- Each product has its own subfolder (e.g., `product1/`, `product2/`).
- Product folders can contain:
  - A `config.yaml` file if special overrides are needed.
  - Additional files or templates specific to the product.

### `output/`
- Default directory for generated documents.
- Generated files follow naming patterns: `[product]_[section]_[LANG]_[date].docx`.

## Configuration
Paths can be customized in the main configuration file:

```yaml
paths:
  base: ./base
  templates: ${base}/templates
  products: ${base}/products
  common: ${base}/common
  output: ${base}/output
```

This structure ensures that:
- Language-specific templates are easily identifiable using ISO-style suffixes.
- Products have dedicated folders for their specific configurations and data.
- Common resources are centralized, promoting reuse across projects.
