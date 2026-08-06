"""Product documents and images."""

from __future__ import annotations

import logging
from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import DocumentType, ImageType
from app.core.storage import Storage
from app.products.models import Document, ProductImage
from app.products.service import get_product

logger = logging.getLogger("app.products")

DOC_SUFFIXES = {".pdf"}
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


def list_documents(db: Session, product_id: UUID) -> list[Document]:
    get_product(db, product_id)
    return list(
        db.scalars(
            select(Document)
            .where(Document.product_id == product_id)
            .order_by(Document.doc_type)
        ).all()
    )


def get_document(db: Session, product_id: UUID, document_id: UUID) -> Document:
    get_product(db, product_id)
    row = db.scalar(
        select(Document).where(
            Document.id == document_id,
            Document.product_id == product_id,
        )
    )
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    return row


def create_document(
    db: Session,
    product_id: UUID,
    *,
    doc_type: DocumentType,
    file: UploadFile,
    storage: Storage,
) -> Document:
    get_product(db, product_id)
    try:
        key, original = storage.save_file(
            product_id=product_id,
            folder="docs",
            upload=file,
            allowed_suffixes=DOC_SUFFIXES,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from None

    row = Document(
        product_id=product_id,
        doc_type=doc_type,
        file_path=key,
        original_filename=original,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    logger.info("document created id=%s product_id=%s", row.id, product_id)
    return row


def delete_document(
    db: Session,
    product_id: UUID,
    document_id: UUID,
    *,
    storage: Storage,
) -> None:
    row = get_document(db, product_id, document_id)
    key = row.file_path
    db.delete(row)
    db.commit()
    storage.delete(key)


def list_images(db: Session, product_id: UUID) -> list[ProductImage]:
    get_product(db, product_id)
    return list(
        db.scalars(
            select(ProductImage)
            .where(ProductImage.product_id == product_id)
            .order_by(ProductImage.sort_order, ProductImage.id)
        ).all()
    )


def get_image(db: Session, product_id: UUID, image_id: UUID) -> ProductImage:
    get_product(db, product_id)
    row = db.scalar(
        select(ProductImage).where(
            ProductImage.id == image_id,
            ProductImage.product_id == product_id,
        )
    )
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found",
        )
    return row


def create_image(
    db: Session,
    product_id: UUID,
    *,
    image_type: ImageType,
    file: UploadFile,
    sort_order: int,
    storage: Storage,
) -> ProductImage:
    get_product(db, product_id)

    if image_type == ImageType.COVER:
        existing = db.scalar(
            select(ProductImage).where(
                ProductImage.product_id == product_id,
                ProductImage.image_type == ImageType.COVER,
            )
        )
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cover image already exists; delete it first",
            )

    try:
        key, _ = storage.save_file(
            product_id=product_id,
            folder="images",
            upload=file,
            allowed_suffixes=IMAGE_SUFFIXES,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from None

    row = ProductImage(
        product_id=product_id,
        image_type=image_type,
        file_path=key,
        sort_order=sort_order,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    logger.info("image created id=%s product_id=%s", row.id, product_id)
    return row


def delete_image(
    db: Session,
    product_id: UUID,
    image_id: UUID,
    *,
    storage: Storage,
) -> None:
    row = get_image(db, product_id, image_id)
    key = row.file_path
    db.delete(row)
    db.commit()
    storage.delete(key)
