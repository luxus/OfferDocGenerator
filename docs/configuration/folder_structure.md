# Default Folder Structure

The default folder structure assumes a root directory where all configuration and assets are stored. This can be overwritten in the main configuration file.

```text
base/
├── templates/               # Main template files (e.g., main_DE.docx, section1_1_EN.docx)
│   ├── common/             # Common template fragments used across sections/languages
│   └── Web Application Security Assessment/  # Product-specific template folder
│       └── section1_1_DE.docx  # Example template file with language suffix
├── common/                 # Shared DOCX files, images, or other assets
└── output/                 # Generated documents
```

## Explanation of Folders

### `templates/`
- Contains the main template files
- Templates use language suffixes in filenames (e.g., `_EN.docx`, `_DE.docx`)
- Product-specific templates go in their own subfolders
- The `common/` subfolder contains reusable DOCX fragments

### `common/`
- Shared resources used across multiple templates
- Contains:
  - Images and media files
  - Style definitions
  - Common DOCX fragments
  - Shared configuration files

### `output/`
- Default directory for generated documents
- Generated files follow naming pattern: `[product]_[section]_[LANG]_[date].docx`

## Configuration
Paths can be customized in the main configuration file:

```yaml
paths:
  base: ./base
  templates: ${base}/templates
  common: ${base}/common
  output: ${base}/output
```
