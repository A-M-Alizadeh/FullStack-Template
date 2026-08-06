"""Sustainability schemas."""

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SustainabilityUpsert(BaseModel):
    carbon_footprint: str = Field(min_length=1, max_length=100)
    water_consumption: str = Field(min_length=1, max_length=100)
    recycled_material_percent: Decimal = Field(
        ge=0, le=100, max_digits=5, decimal_places=2
    )
    repairability_score: Decimal = Field(ge=0, le=100, max_digits=5, decimal_places=2)
    recyclable: bool = False

    @field_validator("carbon_footprint", "water_consumption")
    @classmethod
    def strip_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be empty")
        return value


class SustainabilityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_id: UUID
    carbon_footprint: str
    water_consumption: str
    recycled_material_percent: Decimal
    repairability_score: Decimal
    recyclable: bool
