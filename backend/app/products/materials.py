"""Materials nested under a product."""

from __future__ import annotations

import logging
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.products.models import Material
from app.products.service import get_product
from app.schemas.materials import MaterialCreate, MaterialUpdate

logger = logging.getLogger("app.products")


def list_materials(db: Session, product_id: UUID) -> list[Material]:
    get_product(db, product_id)
    return list(
        db.scalars(
            select(Material).where(Material.product_id == product_id).order_by(Material.name)
        ).all()
    )


def get_material(db: Session, product_id: UUID, material_id: UUID) -> Material:
    get_product(db, product_id)
    material = db.scalar(
        select(Material).where(
            Material.id == material_id,
            Material.product_id == product_id,
        )
    )
    if material is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found",
        )
    return material


def create_material(
    db: Session, product_id: UUID, *, data: MaterialCreate
) -> Material:
    get_product(db, product_id)
    material = Material(product_id=product_id, **data.model_dump())
    db.add(material)
    db.commit()
    db.refresh(material)
    logger.info("material created id=%s product_id=%s", material.id, product_id)
    return material


def update_material(
    db: Session,
    product_id: UUID,
    material_id: UUID,
    *,
    data: MaterialUpdate,
) -> Material:
    material = get_material(db, product_id, material_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(material, field, value)
    db.commit()
    db.refresh(material)
    return material


def delete_material(db: Session, product_id: UUID, material_id: UUID) -> None:
    material = get_material(db, product_id, material_id)
    db.delete(material)
    db.commit()
    logger.info("material deleted id=%s", material_id)
