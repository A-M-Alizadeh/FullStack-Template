"""Product CRUD logic."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.audit import service as audit_service
from app.core.cache import invalidate_stats_cache
from app.core.config import get_settings
from app.core.enums import ImageType, PassportStatus, ProductStatus
from app.products.models import Passport, Product, ProductImage, QrScan
from app.schemas.products import (
    ProductCoverImage,
    ProductCreate,
    ProductListResponse,
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


def _active_passports_by_product(
    db: Session, product_ids: list[UUID]
) -> dict[UUID, Passport]:
    if not product_ids:
        return {}
    rows = db.scalars(
        select(Passport).where(
            Passport.product_id.in_(product_ids),
            Passport.status == PassportStatus.ACTIVE,
        )
    ).all()
    return {row.product_id: row for row in rows}


def _scan_counts_by_product(
    db: Session, product_ids: list[UUID]
) -> dict[UUID, int]:
    """Sum QR scans across all passport versions for each product."""
    if not product_ids:
        return {}
    rows = db.execute(
        select(Passport.product_id, func.count(QrScan.id))
        .join(QrScan, QrScan.passport_id == Passport.id)
        .where(Passport.product_id.in_(product_ids))
        .group_by(Passport.product_id)
    ).all()
    return {product_id: int(count) for product_id, count in rows}


def _cover_url(product_id: UUID, image_id: UUID) -> str:
    prefix = get_settings().api_prefix.rstrip("/")
    return f"{prefix}/products/{product_id}/images/{image_id}/file"


def to_response(
    product: Product,
    cover: ProductImage | None = None,
    *,
    passport: Passport | None = None,
    scan_count: int = 0,
) -> ProductResponse:
    payload = ProductResponse.model_validate(product)
    updates: dict = {
        "public_uuid": passport.public_uuid if passport is not None else None,
        "scan_count": scan_count,
    }
    if cover is not None:
        updates["cover_image"] = ProductCoverImage(
            id=cover.id,
            url=_cover_url(product.id, cover.id),
        )
    return payload.model_copy(update=updates)


def _enrich_products(db: Session, products: list[Product]) -> list[ProductResponse]:
    ids = [p.id for p in products]
    covers = _covers_by_product(db, ids)
    passports = _active_passports_by_product(db, ids)
    scan_counts = _scan_counts_by_product(db, ids)
    return [
        to_response(
            p,
            covers.get(p.id),
            passport=passports.get(p.id),
            scan_count=scan_counts.get(p.id, 0),
        )
        for p in products
    ]


def _active_filter():
    return Product.deleted_at.is_(None)


def list_products(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 50,
    q: str | None = None,
    status_filter: ProductStatus | None = None,
) -> ProductListResponse:
    stmt = select(Product).where(_active_filter())
    count_stmt = select(func.count()).select_from(Product).where(_active_filter())

    if status_filter is not None:
        stmt = stmt.where(Product.status == status_filter)
        count_stmt = count_stmt.where(Product.status == status_filter)

    if q:
        term = f"%{q.strip()}%"
        search = or_(
            Product.name.ilike(term),
            Product.sku.ilike(term),
            Product.serial_number.ilike(term),
            Product.description.ilike(term),
        )
        stmt = stmt.where(search)
        count_stmt = count_stmt.where(search)

    total = int(db.scalar(count_stmt) or 0)
    products = list(
        db.scalars(
            stmt.order_by(Product.created_at.desc()).offset(skip).limit(limit)
        ).all()
    )
    return ProductListResponse(
        items=_enrich_products(db, products),
        total=total,
        skip=skip,
        limit=limit,
    )


def get_product(db: Session, product_id: UUID) -> Product:
    product = db.get(Product, product_id)
    if product is None or product.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    return product


def get_product_response(db: Session, product_id: UUID) -> ProductResponse:
    product = get_product(db, product_id)
    return _enrich_products(db, [product])[0]


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
        db.flush()
    except IntegrityError:
        db.rollback()
        logger.info("create product failed sku=%s", data.sku)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="SKU already exists",
        ) from None
    audit_service.record(
        db,
        actor_user_id=user.id,
        action="product.create",
        entity_type="product",
        entity_id=product.id,
        details={"sku": product.sku, "name": product.name},
    )
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
                _active_filter(),
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


def delete_product(
    db: Session, product_id: UUID, *, actor_id: UUID
) -> None:
    """Soft-delete: hide from lists; keep row + passport history."""
    product = get_product(db, product_id)
    product.deleted_at = datetime.now(UTC)
    audit_service.record(
        db,
        actor_user_id=actor_id,
        action="product.delete",
        entity_type="product",
        entity_id=product.id,
        details={"sku": product.sku, "name": product.name},
    )
    db.commit()
    invalidate_stats_cache()
    logger.info("product soft-deleted id=%s", product_id)


def restore_product(
    db: Session, product_id: UUID, *, actor_id: UUID
) -> ProductResponse:
    """Clear soft-delete so the product returns to lists."""
    product = db.get(Product, product_id)
    if product is None or product.deleted_at is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deleted product not found",
        )

    conflict = db.scalar(
        select(Product.id).where(
            Product.sku == product.sku,
            Product.id != product.id,
            _active_filter(),
        )
    )
    if conflict is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="SKU already exists on another product; change that SKU first",
        )

    product.deleted_at = None
    audit_service.record(
        db,
        actor_user_id=actor_id,
        action="product.restore",
        entity_type="product",
        entity_id=product.id,
        details={"sku": product.sku, "name": product.name},
    )
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="SKU already exists on another product; change that SKU first",
        ) from None
    db.refresh(product)
    invalidate_stats_cache()
    logger.info("product restored id=%s", product_id)
    return get_product_response(db, product.id)
