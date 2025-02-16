# Variables Documentation

## Variable Format
Variables in templates use the double curly brace syntax:
- Format: `{{ variable_name }}`
- Example: `{{ customer_address }}`

## Supported Variables

### Customer Information
```yaml
customer:
  address: "{{ customer_address }}"
  company: "{{ customer_company }}"
  email: "{{ customer_email }}"
```

### Sales Information
```yaml
sales:
  phone: "{{ sales_phone }}"
  representative: "{{ sales_rep }}"
```

## Multi-Language Support
Variables can have different values for each supported language:

```yaml
multi_language_variables:
  en:
    customer_address: "123 Main St, City"
    customer_company: "Example Inc."
  de:
    customer_address: "Musterstraße 45, Stadt"
    customer_company: "Beispiel GmbH"
```

## Variable Rules
1. Use underscores for variable names (e.g., `customer_address`)
2. Avoid spaces in variable names
3. Use lowercase for consistency
4. Define all variables in the configuration file
5. Provide values for all supported languages
