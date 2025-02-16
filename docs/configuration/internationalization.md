# Internationalization

## Language Configuration

Configure supported languages and currency format in the configuration file:

```yaml
internationalization:
  default_language: en
  supported_languages: [en, de, fr]
  currency_format: EUR
```

## Variable Naming Convention

- Variables must use the `{{ variable_name }}` format in DOCX templates.
- Avoid dot notation (e.g., `customer.address`) due to Jinja2 limitations; use underscores instead (e.g., `customer_address`).
- Multi-language variables are defined under their respective language codes:

```yaml
multi_language_variables:
  en:
    customer_address: "123 Main St"
    sales_phone: "+49 123 456789"
  de:
    customer_address: "Musterstraße 45"
    sales_phone: "+49 123 456789"
```

## Multi-Language Variables Example

Define variables for multiple languages in the configuration file:

```yaml
multi_language_variables:
  en:
    greeting: "Hello"
    company_name: "Example Inc."
  de:
    greeting: "Hallo"
    company_name: "Beispiel GmbH"
```

When generating a document, the system will automatically select the appropriate language-specific variable. If no language-specific value is defined, it falls back to the default language.

## Currency Handling

- Use standard currency codes (e.g., `CHF`, `EUR`, `USD`).
- Format numbers according to locale conventions. For example:
   ```yaml
   internationalization:
     default_language: en
     supported_languages: [en, de, fr]
     currency_format: EUR
   ```

## Date Formats

- Use ISO date formats (YYYY-MM-DD).
- Convert dates to locale-specific formats where applicable.
- Include timezone information when needed.

Example in YAML configuration:

```yaml
date_formats:
  default: "%Y-%m-%d"
  de: "%d.%m.%Y"
```

## Fallback Mechanism

If a required variable is not defined for the current language, the system checks the default language configuration. If no default value exists, an error is thrown.

Example:

- Variable `greeting` is defined only in English.
- When generating a document in German, the system uses the English greeting as fallback.

## Best Practices

### 1. Language Codes
- Use standard ISO language codes (e.g., 'en', 'de', 'fr').
- Always include the default language.
- Define all variables for all supported languages if applicable.

### 2. Currency Handling
- Use standard currency codes and format numbers according to locale preferences.

### 3. Date Formats
- Use ISO date formats and localize when necessary.
