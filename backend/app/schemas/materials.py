"""Material schemas."""

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.common import normalize_country_code


class MaterialCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    percentage: Decimal = Field(ge=0, le=100, max_digits=5, decimal_places=2)
    country_of_origin: str = Field(min_length=2, max_length=2)
    recyclable: bool = False

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be empty")
        return value

    @field_validator("country_of_origin")
    @classmethod
    def country(cls, value: str) -> str:
        return normalize_country_code(value)


class MaterialUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    percentage: Decimal | None = Field(
        default=None, ge=0, le=100, max_digits=5, decimal_places=2
    )
    country_of_origin: str | None = Field(default=None, min_length=2, max_length=2)
    recyclable: bool | None = None

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("must not be empty")
        return value

    @field_validator("country_of_origin")
    @classmethod
    def country(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return normalize_country_code(value)


class MaterialResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_id: UUID
    name: str
    percentage: Decimal
    country_of_origin: str
    recyclable: bool
