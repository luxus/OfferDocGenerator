# Default Folder Structure

The default folder structure assumes a root directory where all configuration and assets are stored. This can be overwritten in the main configuration file.

```text
base/
├── templates/               # Main template files (e.g., main_DE.docx, section1_1_EN.docx)
│   ├── [language]/         # Optional: language-specific templates
│   └── common/             # Common template fragments used across sections/languages
│       └── section1_2.docx # Example fragment
├── products/               # Product-specific configuration and data (optional)
│   └── [product_name]/     # Folder for product-specific settings
│       └── config.yaml     # Only needed if product requires special configuration
├── common/                 # Shared DOCX files, images, or other assets
└── output/                 # Generated documents
```

## Explanation of Folders

### `templates/`
- Contains the main template files
- Naming convention: `[section]_[subsection]_[LANG].docx`
- Language-specific templates go in subfolders (e.g., `templates/en/`, `templates/de/`)
- The `common/` subfolder contains reusable DOCX fragments

### `products/`
- Optional folder for product-specific configuration
- Only needed if a product requires special settings or overrides
- Each product folder can contain:
  - `config.yaml`: Custom variables and settings
  - `templates/`: Product-specific template overrides
  - `assets/`: Product-specific images or resources

### `common/`
- Shared resources used across multiple templates
- Contains:
  - Images and media files
  - Style definitions
  - Common DOCX fragments
  - Shared configuration files

### `output/`
- Default directory for generated documents
- Maintains source folder structure
- Files named according to template: `[product]_[section]_[LANG]_[date].docx`

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
