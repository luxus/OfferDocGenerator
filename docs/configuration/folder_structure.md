# Default Folder Structure

The default folder structure is organized to separate concerns clearly and support automatic detection of files based on naming conventions.

```text
base/
├── templates/                 # Main template files (e.g., base_en.docx, section1_2_de.docx)
├── products/                 # Product-specific configuration and data
│   ├── Web Application Security Assessment/  # Example product folder
│   │   ├── section_1_1_de.docx      # Product-specific document fragments
│   │   ├── section_1_2_en.docx      # More product-specific fragments
│   │   ├── section_1_3_de.docx      # Yet more fragments
│   │   ├── section_1_3_en.docx      # Yet more fragments
│   │   ├── config.yaml      # Product-specific configuration (optional)
│   └── Another Product/      # Another product example
├── common/                   # Shared DOCX fragments and assets used across all products
├── output/                   # Final output documents
└── generated/                # Temporary generated documents and samples
```

## Explanation of Folders

### `templates/`

- Contains the main template files.
- Templates use language suffixes in filenames (e.g., `_en.docx`, `_de.docx`).
- Product-specific templates are stored directly under `templates/`.

### `common/`

- Shared resources used across all products and sections.
- Includes:
  - Images and media files
  - Style definitions
  - Common DOCX fragments

### `products/`

- Folder for product-specific configurations and data.
- Each product has its own subfolder (e.g., `Web Application Security Assessment/`, `Another Product/`).
- Product folders can contain:
  - A `config.yaml` file if special overrides are needed.
  - Additional files or templates specific to the product.

### `output/`

- Default directory for generated documents.
- Generated files follow naming patterns: `[prefix]_[product]_[lang][CURRENCY].docx`.

## Configuration and Internationalization

The main configuration file defines paths and settings:

```yaml
# config.yaml
prefix: Offer
paths:
  base: ./base # Root directory for all other folders
  templates: ${base}/templates # Main template files
  common: ${base}/common # Shared DOCX fragments and assets
  products: ${base}/products # Product-specific configurations
  output: ${base}/output # Final output directory
  generated: ${base}/generated # Temporary generated files

internationalization:
  default_language: en # Default language code
  supported_languages: [en, de, fr] # List of supported languages
```

## Variable Handling and Multi-Language Support

- **Variables in DOCX Files**:

  - Use placeholders like `{{ variable_name }}` in DOCX files.
  - Avoid dot notation (e.g., `customer.address`); use underscores instead (e.g., `customer_address`).

- **Multi-Language Variables**:
  - Define variables with language-specific suffixes if necessary:
  ```yaml
  variables:
    customer:
      city: "Munich" # Default value (fallback)
      city_de: "München" # German override
  ```
  - System checks for language-specific variables first (e.g., `city_de`), then falls back to default.

## File Naming Conventions

- **Templates**:

  - Use language codes as suffixes (e.g., `base_en.docx`, `section1_2_de.docx`).
  - Enables automatic detection based on current language.

- **Products**:
  - Product-specific files go directly under their respective product folders.
  - Example: `products/Web Application Security Assessment/section1_2_de.docx`.

## Best Practices

- Keep templates modular by using common fragments for shared content.
- Maintain consistent naming conventions for automatic detection.
- Regularly review configuration to ensure paths and settings align with project structure.
