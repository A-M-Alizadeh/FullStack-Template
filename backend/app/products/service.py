"""Product CRUD logic."""

from __future__ import annotations

import logging
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.enums import ImageType, ProductStatus
from app.products.models import Product, ProductImage
from app.schemas.products import (
    ProductCoverImage,
    ProductCreate,
    ProductResponse,
    ProductUpdate,
)
from app.users.models import User

logger = logging.getLogger("app.products")


def _covers_by_product(
    db: Session, product_ids: list[UUID]
) -> dict[UUID, ProductImage]:
    if not product_ids:
        return {}
    rows = db.scalars(
        select(ProductImage).where(
            ProductImage.product_id.in_(product_ids),
            ProductImage.image_type == ImageType.COVER,
        )
    ).all()
    return {row.product_id: row for row in rows}


def _cover_url(product_id: UUID, image_id: UUID) -> str:
    prefix = get_settings().api_prefix.rstrip("/")
    return f"{prefix}/products/{product_id}/images/{image_id}/file"


def to_response(
    product: Product, cover: ProductImage | None = None
) -> ProductResponse:
    payload = ProductResponse.model_validate(product)
    if cover is None:
        return payload
    return payload.model_copy(
        update={
            "cover_image": ProductCoverImage(
                id=cover.id,
                url=_cover_url(product.id, cover.id),
            )
        }
    )


def list_products(db: Session, *, skip: int = 0, limit: int = 50) -> list[ProductResponse]:
    products = list(
        db.scalars(
            select(Product).order_by(Product.created_at.desc()).offset(skip).limit(limit)
        ).all()
    )
    covers = _covers_by_product(db, [p.id for p in products])
    return [to_response(p, covers.get(p.id)) for p in products]


def get_product(db: Session, product_id: UUID) -> Product:
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    return product


def get_product_response(db: Session, product_id: UUID) -> ProductResponse:
    product = get_product(db, product_id)
    cover = db.scalar(
        select(ProductImage).where(
            ProductImage.product_id == product.id,
            ProductImage.image_type == ImageType.COVER,
        )
    )
    return to_response(product, cover)


def create_product(db: Session, *, data: ProductCreate, user: User) -> ProductResponse:
    product = Product(
        created_by_id=user.id,
        name=data.name,
        sku=data.sku,
        serial_number=data.serial_number,
        category=data.category,
        description=data.description,
        production_date=data.production_date,
        country_of_origin=data.country_of_origin,
        status=ProductStatus.DRAFT,
    )
    db.add(product)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        logger.info("create product failed sku=%s", data.sku)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="SKU already exists",
        ) from None
    db.refresh(product)
    logger.info("product created id=%s sku=%s", product.id, product.sku)
    return to_response(product)


def update_product(
    db: Session,
    product_id: UUID,
    *,
    data: ProductUpdate,
) -> ProductResponse:
    product = get_product(db, product_id)
    changes = data.model_dump(exclude_unset=True)
    if not changes:
        return get_product_response(db, product_id)

    if "sku" in changes and changes["sku"] != product.sku:
        exists = db.scalar(
            select(Product.id).where(
                Product.sku == changes["sku"],
                Product.id != product.id,
            )
        )
        if exists is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="SKU already exists",
            )

    for field, value in changes.items():
        setattr(product, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="SKU already exists",
        ) from None
    db.refresh(product)
    logger.info("product updated id=%s", product.id)
    return get_product_response(db, product.id)


def delete_product(db: Session, product_id: UUID) -> None:
    product = get_product(db, product_id)
    db.delete(product)
    db.commit()
    logger.info("product deleted id=%s", product_id)
