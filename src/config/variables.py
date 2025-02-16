from typing import Dict, Any
from pydantic import BaseModel, validator

class Variables(BaseModel):
    customer: Dict[str, Any] = {
        "city": "Munich",
        "city_de": "München",
        "city_fr": "Munich"
    }
    sales: Dict[str, Any] = {
        "phone": "+49 123 456789"
    }
    
    @validator("customer", "sales")
    def validate_variables(cls, value: Dict[str, Any]) -> Dict[str, Any]:
        # Ensure all language-specific keys follow the pattern key_lang
        base_keys = {k for k in value.keys() if '_' not in k}
        lang_keys = {k for k in value.keys() if '_' in k}
        
        for key in lang_keys:
            base, lang = key.rsplit('_', 1)
            if base not in base_keys:
                raise ValueError(f"Language-specific key '{key}' has no base key '{base}'")
        
        return value
