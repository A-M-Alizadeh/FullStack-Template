"""Product tables and everything that hangs off a product.

One file on purpose: product + materials + certs + passport stay easy to read together.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import (
    DocumentType,
    ImageType,
    PassportStatus,
    ProductCategory,
    ProductStatus,
    VerificationStatus,
)
from app.database.base import Base

if TYPE_CHECKING:
    from app.users.models import User


class Product(Base):
    """Main back-office product (draft until published)."""

    __tablename__ = "products"
    __table_args__ = (
        # Soft-deleted rows keep their SKU; only active rows must be unique.
        Index(
            "uq_products_sku_active",
            "sku",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    created_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), index=True
    )
    name: Mapped[str] = mapped_column(String(255))
    sku: Mapped[str] = mapped_column(String(100), index=True)
    serial_number: Mapped[str] = mapped_column(String(100))
    category: Mapped[ProductCategory] = mapped_column(
        Enum(
            ProductCategory,
            name="product_category",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
    )
    description: Mapped[str] = mapped_column(Text, default="")
    production_date: Mapped[date] = mapped_column(Date)
    country_of_origin: Mapped[str] = mapped_column(String(2))
    status: Mapped[ProductStatus] = mapped_column(
        Enum(
            ProductStatus,
            name="product_status",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        default=ProductStatus.DRAFT,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    created_by: Mapped[User] = relationship(back_populates="products")
    materials: Mapped[list[Material]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )
    sustainability: Mapped[Sustainability | None] = relationship(
        back_populates="product", cascade="all, delete-orphan", uselist=False
    )
    certifications: Mapped[list[Certification]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )
    documents: Mapped[list[Document]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )
    images: Mapped[list[ProductImage]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )
    passport: Mapped[Passport | None] = relationship(
        back_populates="product", cascade="all, delete-orphan", uselist=False
    )


class Material(Base):
    """One material row for a product (many allowed)."""

    __tablename__ = "materials"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(255))
    percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    country_of_origin: Mapped[str] = mapped_column(String(2))
    recyclable: Mapped[bool] = mapped_column(Boolean, default=False)

    product: Mapped[Product] = relationship(back_populates="materials")


class Sustainability(Base):
    """Env metrics for a product (at most one row)."""

    __tablename__ = "sustainability"
    __table_args__ = (UniqueConstraint("product_id"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), index=True
    )
    carbon_footprint: Mapped[str] = mapped_column(String(100))
    water_consumption: Mapped[str] = mapped_column(String(100))
    recycled_material_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    repairability_score: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    recyclable: Mapped[bool] = mapped_column(Boolean, default=False)

    product: Mapped[Product] = relationship(back_populates="sustainability")


class IssuingAuthority(Base):
    """Lookup: who issued a cert (TÜV, SGS, …)."""

    __tablename__ = "issuing_authorities"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    code: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)

    certifications: Mapped[list[Certification]] = relationship(
        back_populates="issuing_authority"
    )


class CertificationType(Base):
    """Lookup: cert name/type (ISO 9001, CE, …)."""

    __tablename__ = "certification_types"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    code: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)

    certifications: Mapped[list[Certification]] = relationship(
        back_populates="certification_type"
    )


class Certification(Base):
    """A cert on a product: type + authority + dates + PDF path."""

    __tablename__ = "certifications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), index=True
    )
    certification_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("certification_types.id"), index=True
    )
    issuing_authority_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("issuing_authorities.id"), index=True
    )
    issue_date: Mapped[date] = mapped_column(Date)
    expiration_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    pdf_path: Mapped[str] = mapped_column(String(500))

    product: Mapped[Product] = relationship(back_populates="certifications")
    certification_type: Mapped[CertificationType] = relationship(
        back_populates="certifications"
    )
    issuing_authority: Mapped[IssuingAuthority] = relationship(
        back_populates="certifications"
    )


class Document(Base):
    """Uploaded manual / warranty / datasheet."""

    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), index=True
    )
    doc_type: Mapped[DocumentType] = mapped_column(
        Enum(
            DocumentType,
            name="document_type",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
    )
    file_path: Mapped[str] = mapped_column(String(500))
    original_filename: Mapped[str] = mapped_column(String(255))

    product: Mapped[Product] = relationship(back_populates="documents")


class ProductImage(Base):
    """Cover or gallery image path."""

    __tablename__ = "product_images"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), index=True
    )
    image_type: Mapped[ImageType] = mapped_column(
        Enum(
            ImageType,
            name="image_type",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
    )
    file_path: Mapped[str] = mapped_column(String(500))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    product: Mapped[Product] = relationship(back_populates="images")


class Passport(Base):
    """Public passport: stable UUID for /passport/{uuid} + QR file path."""

    __tablename__ = "passports"
    __table_args__ = (UniqueConstraint("product_id"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), index=True
    )
    public_uuid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), unique=True, default=uuid.uuid4, index=True
    )
    qr_code_path: Mapped[str] = mapped_column(String(500))
    version: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[PassportStatus] = mapped_column(
        Enum(
            PassportStatus,
            name="passport_status",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        default=PassportStatus.ACTIVE,
    )
    verification_status: Mapped[VerificationStatus] = mapped_column(
        Enum(
            VerificationStatus,
            name="verification_status",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        default=VerificationStatus.VERIFIED,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    product: Mapped[Product] = relationship(back_populates="passport")
    scans: Mapped[list[QrScan]] = relationship(
        back_populates="passport", cascade="all, delete-orphan"
    )


class QrScan(Base):
    """One analytics row when someone opens/scans the passport."""

    __tablename__ = "qr_scans"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    passport_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("passports.id", ondelete="CASCADE"), index=True
    )
    scanned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    ip_address: Mapped[str] = mapped_column(String(45))
    browser: Mapped[str] = mapped_column(String(100))
    operating_system: Mapped[str] = mapped_column(String(100))
    browser_language: Mapped[str] = mapped_column(String(20))
    country: Mapped[str] = mapped_column(String(2))

    passport: Mapped[Passport] = relationship(back_populates="scans")
