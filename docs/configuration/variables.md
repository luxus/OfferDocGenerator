# Template Variables

## Variable Syntax
All variables in DOCX templates must use the double curly brace syntax:
```
{{ variable_name }}
```

## Naming Conventions

### Basic Rules
1. Use lowercase letters and underscores
2. No spaces or special characters
3. Be descriptive and specific
4. Use prefixes for categorization

### Examples
✅ Good variable names:
- `customer_address`
- `invoice_total_amount`
- `project_start_date`

❌ Avoid:
- `customerAddress` (use underscores)
- `Customer Address` (no spaces)
- `var1` (not descriptive)

## Multi-Language Support

### Language-Specific Variables
Variables can be defined per language using suffixes:
```yaml
# In config.yaml
variables:
  company_name_en: "Example Corp"
  company_name_de: "Beispiel GmbH"
  address_en: "123 Main St"
  address_de: "Hauptstraße 123"
```

### Default Values
Always provide a default value without language suffix:
```yaml
company_name: "Example Corp"  # Fallback value
```

## Variable Categories

### Customer Information
- `customer_name`
- `customer_address`
- `customer_email`
- `customer_phone`

### Project Details
- `project_name`
- `project_start_date`
- `project_end_date`
- `project_manager`

### Financial Information
- `invoice_number`
- `total_amount`
- `currency_code`

## Configuration Example
```yaml
variables:
  # Default values
  customer_name: "Example Corp"
  project_name: "Security Assessment"
  
  # Language-specific values
  en:
    customer_name: "Example Corporation"
    project_name: "Security Assessment Project"
  de:
    customer_name: "Beispiel GmbH"
    project_name: "Sicherheitsbewertungsprojekt"
```
