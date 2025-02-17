from typing import Dict, Any, TypeGuard, assert_type
from pydantic import BaseModel, field_validator, Field, ConfigDict
from enum import Enum, auto

class Language(str, Enum):
    EN = "en"
    DE = "de"
    FR = "fr"

class LocalizedText(BaseModel):
    default: str
    translations: Dict[Language, str] = Field(default_factory=dict)

    model_config = ConfigDict(frozen=True, validate_default=True)

    @field_validator("translations")
    @classmethod
    def validate_translations(cls, v: Dict[Language, str]) -> Dict[Language, str]:
        supported_languages = {lang for lang in Language}
        if invalid_langs := set(v.keys()) - supported_languages:
            raise ValueError(f"Unsupported languages: {invalid_langs}")
        return v

class CustomerInfo(BaseModel):
    name: LocalizedText
    city: LocalizedText
    address: LocalizedText
    country: LocalizedText

    model_config = ConfigDict(frozen=True, validate_default=True)

class SalesInfo(BaseModel):
    name: str
    phone: str
    email: str

    model_config = ConfigDict(frozen=True, validate_default=True)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if "@" not in v or "." not in v:
            raise ValueError("Invalid email format")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not v.startswith("+"):
            raise ValueError("Phone number must start with '+'")
        if not v[1:].replace(" ", "").isdigit():
            raise ValueError("Invalid phone number format")
        return v

class Variables(BaseModel):
    customer: Dict[str, Any] = Field(
        default_factory=lambda: {
            "city": "Munich",
            "city_de": "München",
            "city_fr": "Munich"
        }
    )
    sales: Dict[str, Any] = Field(
        default_factory=lambda: {
            "phone": "+49 123 456789"
        }
    )

    model_config = ConfigDict(frozen=True, validate_default=True)

    @field_validator("customer", "sales")
    @classmethod
    def validate_variables(cls, value: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(value, dict):
            raise ValueError("Variables must be a dictionary")
        return value

    def is_valid_customer_info(self, data: Any) -> TypeGuard[CustomerInfo]:
        if isinstance(data, dict):
            required_fields = {"name", "city", "address", "country"}
            return all(
                isinstance(data.get(field), LocalizedText)
                for field in required_fields
            )
        return False
    
    def validate_customer(self, data: Any) -> CustomerInfo:
        if self.is_valid_customer_info(data):
            assert_type(data, CustomerInfo)
            return data
        raise ValueError("Invalid customer info")
