"""Document and image response schemas."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.core.enums import DocumentType, ImageType


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_id: UUID
    doc_type: DocumentType
    file_path: str
    original_filename: str


class ImageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_id: UUID
    image_type: ImageType
    file_path: str
    sort_order: int
