"""Passport / publish / public page shapes."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.core.enums import (
    DocumentType,
    ImageType,
    PassportStatus,
    ProductCategory,
    ProductStatus,
    VerificationStatus,
)


class PassportSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    public_uuid: UUID
    version: int
    status: PassportStatus
    verification_status: VerificationStatus
    public_url: str
    qr_code_url: str
    created_at: datetime


class PublishResponse(BaseModel):
    product_id: UUID
    status: ProductStatus
    passport: PassportSummary


class PublicMaterial(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    percentage: Decimal
    country_of_origin: str
    recyclable: bool


class PublicSustainability(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    carbon_footprint: str
    water_consumption: str
    recycled_material_percent: Decimal
    repairability_score: Decimal
    recyclable: bool


class PublicCertification(BaseModel):
    name: str
    issuing_authority: str
    issue_date: date
    expiration_date: date | None
    pdf_url: str


class PublicDocument(BaseModel):
    doc_type: DocumentType
    original_filename: str
    file_url: str


class PublicImage(BaseModel):
    id: UUID
    image_type: ImageType
    sort_order: int
    file_url: str


class PublicProduct(BaseModel):
    name: str
    sku: str
    serial_number: str
    category: ProductCategory
    description: str
    production_date: date
    country_of_origin: str


class PublicPassportResponse(BaseModel):
    public_uuid: UUID
    version: int
    status: PassportStatus
    verification_status: VerificationStatus
    created_at: datetime
    product: PublicProduct
    materials: list[PublicMaterial]
    sustainability: PublicSustainability | None
    certifications: list[PublicCertification]
    documents: list[PublicDocument]
    images: list[PublicImage]
