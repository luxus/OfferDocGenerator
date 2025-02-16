# Configuration Reference

The ODG tool uses a YAML configuration file (`config.yaml`) that defines all aspects of your offer document generation. Templates support Jinja2 syntax for dynamic content generation.

## Required Sections

### Offer Details
```yaml
offer:
  number: OFFER-2025-02-16  # Auto-generated based on date
  date: 2025-02-16
  validity:
    en: "30 days"
    de: "30 Tage"
```

### Project Settings
```yaml
settings:
  base_path: /path/to/project
  folders:
    templates: ./templates
    common: ./common
    products: ./products
    output: ./output
  output_prefix: DOC-
```

### Internationalization
```yaml
internationalization:
  default_language: en
  supported_languages: [en, de, fr]
  currency_format: EUR
```

### Customer Information
```yaml
customer:
  name: Test Company
  address: 123 Main St
  city: Test City
  zip: 12345
  country: Test Country
```

### Sales Contact
```yaml
sales:
  name: John Doe
  email: john.doe@example.com
  phone: +1 234 567 890
```

## Configuration Validation

The configuration is automatically validated when:
1. Creating a new project with `odg create`
2. Loading an existing configuration file

Required fields are checked and appropriate error messages are displayed if validation fails.
