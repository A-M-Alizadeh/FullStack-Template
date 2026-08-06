"""Sustainability nested under a product (one row max)."""

from __future__ import annotations

import logging
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.products.models import Sustainability
from app.products.service import get_product
from app.schemas.sustainability import SustainabilityUpsert

logger = logging.getLogger("app.products")


def get_sustainability(db: Session, product_id: UUID) -> Sustainability:
    get_product(db, product_id)
    row = db.scalar(
        select(Sustainability).where(Sustainability.product_id == product_id)
    )
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sustainability not found",
        )
    return row


def upsert_sustainability(
    db: Session, product_id: UUID, *, data: SustainabilityUpsert
) -> Sustainability:
    get_product(db, product_id)
    row = db.scalar(
        select(Sustainability).where(Sustainability.product_id == product_id)
    )
    if row is None:
        row = Sustainability(product_id=product_id, **data.model_dump())
        db.add(row)
    else:
        for field, value in data.model_dump().items():
            setattr(row, field, value)
    db.commit()
    db.refresh(row)
    logger.info("sustainability upserted product_id=%s", product_id)
    return row


def delete_sustainability(db: Session, product_id: UUID) -> None:
    row = get_sustainability(db, product_id)
    db.delete(row)
    db.commit()
    logger.info("sustainability deleted product_id=%s", product_id)
