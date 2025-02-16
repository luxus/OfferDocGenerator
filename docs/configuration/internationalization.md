# Internationalization

## Language Configuration
Configure supported languages in the configuration file:

```yaml
internationalization:
  default_language: en
  supported_languages: [en, de, fr]
  currency_format: EUR
```

## Multi-Language Variables
Variables support different values for each language:

```yaml
multi_language_variables:
  en:
    greeting: "Hello"
    company_name: "Example Inc."
  de:
    greeting: "Hallo"
    company_name: "Beispiel GmbH"
```

## Best Practices

### 1. Language Codes
- Use standard ISO language codes (e.g., 'en', 'de', 'fr')
- Always include the default language
- Define all variables for all supported languages

### 2. Currency Handling
- Use standard currency codes (e.g., 'EUR', 'USD')
- Format numbers according to locale conventions
- Include currency symbols in templates

### 3. Date Formats
- Use ISO date formats (YYYY-MM-DD)
- Convert dates based on locale preferences
- Include timezone information when relevant

### 4. Text Direction
- Support RTL (Right-to-Left) languages when needed
- Use appropriate CSS/styling for RTL content
- Test templates with RTL content
