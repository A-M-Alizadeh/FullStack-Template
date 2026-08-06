"""Certification lookups and product certifications."""

from __future__ import annotations

import logging
from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.storage import Storage
from app.products.models import Certification, CertificationType, IssuingAuthority
from app.products.service import get_product
from app.schemas.certifications import CertificationCreate, CertificationUpdate

logger = logging.getLogger("app.products")

PDF_SUFFIXES = {".pdf"}


def list_certification_types(db: Session) -> list[CertificationType]:
    return list(
        db.scalars(select(CertificationType).order_by(CertificationType.name)).all()
    )


def list_issuing_authorities(db: Session) -> list[IssuingAuthority]:
    return list(
        db.scalars(select(IssuingAuthority).order_by(IssuingAuthority.name)).all()
    )


def _require_type(db: Session, type_id: UUID) -> CertificationType:
    row = db.get(CertificationType, type_id)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unknown certification type",
        )
    return row


def _require_authority(db: Session, authority_id: UUID) -> IssuingAuthority:
    row = db.get(IssuingAuthority, authority_id)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unknown issuing authority",
        )
    return row


def list_certifications(db: Session, product_id: UUID) -> list[Certification]:
    get_product(db, product_id)
    return list(
        db.scalars(
            select(Certification)
            .where(Certification.product_id == product_id)
            .options(
                joinedload(Certification.certification_type),
                joinedload(Certification.issuing_authority),
            )
            .order_by(Certification.issue_date.desc())
        )
        .unique()
        .all()
    )


def get_certification(
    db: Session, product_id: UUID, certification_id: UUID
) -> Certification:
    get_product(db, product_id)
    row = db.scalar(
        select(Certification)
        .where(
            Certification.id == certification_id,
            Certification.product_id == product_id,
        )
        .options(
            joinedload(Certification.certification_type),
            joinedload(Certification.issuing_authority),
        )
    )
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certification not found",
        )
    return row


def create_certification(
    db: Session,
    product_id: UUID,
    *,
    data: CertificationCreate,
    pdf: UploadFile,
    storage: Storage,
) -> Certification:
    get_product(db, product_id)
    _require_type(db, data.certification_type_id)
    _require_authority(db, data.issuing_authority_id)

    try:
        key, _original = storage.save_file(
            product_id=product_id,
            folder="certs",
            upload=pdf,
            allowed_suffixes=PDF_SUFFIXES,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from None

    row = Certification(
        product_id=product_id,
        certification_type_id=data.certification_type_id,
        issuing_authority_id=data.issuing_authority_id,
        issue_date=data.issue_date,
        expiration_date=data.expiration_date,
        pdf_path=key,
    )
    db.add(row)
    db.commit()
    return get_certification(db, product_id, row.id)


def update_certification(
    db: Session,
    product_id: UUID,
    certification_id: UUID,
    *,
    data: CertificationUpdate,
    pdf: UploadFile | None,
    storage: Storage,
) -> Certification:
    row = get_certification(db, product_id, certification_id)
    changes = data.model_dump(exclude_unset=True)

    if "certification_type_id" in changes:
        _require_type(db, changes["certification_type_id"])
    if "issuing_authority_id" in changes:
        _require_authority(db, changes["issuing_authority_id"])

    for field, value in changes.items():
        setattr(row, field, value)

    if pdf is not None and pdf.filename:
        try:
            key, _ = storage.save_file(
                product_id=product_id,
                folder="certs",
                upload=pdf,
                allowed_suffixes=PDF_SUFFIXES,
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from None
        old = row.pdf_path
        row.pdf_path = key
        db.commit()
        storage.delete(old)
    else:
        db.commit()

    return get_certification(db, product_id, certification_id)


def delete_certification(
    db: Session,
    product_id: UUID,
    certification_id: UUID,
    *,
    storage: Storage,
) -> None:
    row = get_certification(db, product_id, certification_id)
    key = row.pdf_path
    db.delete(row)
    db.commit()
    storage.delete(key)
    logger.info("certification deleted id=%s", certification_id)
