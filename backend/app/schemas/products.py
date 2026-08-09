"""Product request/response shapes."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.enums import ProductCategory, ProductStatus
from app.schemas.common import normalize_country_code


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    sku: str = Field(min_length=1, max_length=100)
    serial_number: str = Field(min_length=1, max_length=100)
    category: ProductCategory
    description: str = ""
    production_date: date
    country_of_origin: str = Field(min_length=2, max_length=2)

    @field_validator("sku", "serial_number")
    @classmethod
    def strip_required(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be empty")
        return value

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be empty")
        return value

    @field_validator("country_of_origin")
    @classmethod
    def normalize_country(cls, value: str) -> str:
        return normalize_country_code(value)


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    sku: str | None = Field(default=None, min_length=1, max_length=100)
    serial_number: str | None = Field(default=None, min_length=1, max_length=100)
    category: ProductCategory | None = None
    description: str | None = None
    production_date: date | None = None
    country_of_origin: str | None = Field(default=None, min_length=2, max_length=2)

    @field_validator("sku", "serial_number", "name")
    @classmethod
    def strip_optional(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("must not be empty")
        return value

    @field_validator("country_of_origin")
    @classmethod
    def normalize_country(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return normalize_country_code(value)


class ProductCoverImage(BaseModel):
    """Light cover pointer for list/detail cards."""

    id: UUID
    url: str


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_by_id: UUID
    name: str
    sku: str
    serial_number: str
    category: ProductCategory
    description: str
    production_date: date
    country_of_origin: str
    status: ProductStatus
    created_at: datetime
    updated_at: datetime
    cover_image: ProductCoverImage | None = None
    public_uuid: UUID | None = None
    scan_count: int = 0


class ProductListResponse(BaseModel):
    """Paginated product list."""

    items: list[ProductResponse]
    total: int
    skip: int
    limit: int
