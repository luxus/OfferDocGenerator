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
4. Use language suffixes for translations

### Examples
✅ Good variable names:
- `customer_address`
- `invoice_total_amount`
- `project_start_date`
- `company_name_de` (German translation)
- `address_en` (English translation)

❌ Avoid:
- `customerAddress` (use underscores)
- `Customer Address` (no spaces)
- `var1` (not descriptive)
- `de_company_name` (suffix goes at end)

## Multi-Language Support

### Language-Specific Variables
Add language code suffixes to variable names:
```yaml
# In config.yaml
variables:
  company_name: "Example Corp"      # Default fallback
  company_name_de: "Beispiel GmbH"  # German version
  company_name_fr: "Exemple SARL"   # French version
  
  address: "123 Main St"           # Default fallback
  address_de: "Hauptstraße 123"    # German version
```

### Variable Resolution
1. System checks for language-specific version first (e.g., `company_name_de`)
2. Falls back to default version if not found (e.g., `company_name`)

## Common Variable Categories

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
  # Default values (fallbacks)
  customer_name: "Example Corp"
  project_name: "Security Assessment"
  
  # Language-specific values
  customer_name_de: "Beispiel GmbH"
  customer_name_fr: "Exemple SARL"
  
  project_name_de: "Sicherheitsbewertung"
  project_name_fr: "Évaluation de Sécurité"
```
