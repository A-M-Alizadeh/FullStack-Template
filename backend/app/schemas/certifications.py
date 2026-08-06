"""Certification + lookup schemas."""

from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class LookupResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    name: str


class CertificationCreate(BaseModel):
    certification_type_id: UUID
    issuing_authority_id: UUID
    issue_date: date
    expiration_date: date | None = None


class CertificationUpdate(BaseModel):
    certification_type_id: UUID | None = None
    issuing_authority_id: UUID | None = None
    issue_date: date | None = None
    expiration_date: date | None = None


class CertificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_id: UUID
    certification_type_id: UUID
    issuing_authority_id: UUID
    issue_date: date
    expiration_date: date | None
    pdf_path: str
    certification_type: LookupResponse
    issuing_authority: LookupResponse
