"""Publish products and serve public passports."""

from __future__ import annotations

import logging
import re
import uuid
from uuid import UUID

from fastapi import HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload, selectinload

from app.audit import service as audit_service
from app.core.cache import invalidate_stats_cache
from app.core.config import Settings, get_settings
from app.core.enums import PassportStatus, ProductStatus, VerificationStatus
from app.core.qrcode_util import make_qr_png
from app.core.storage import Storage, get_storage
from app.database.session import SessionLocal
from app.passport.pdf import build_passport_pdf
from app.products.models import (
    Certification,
    Document,
    Passport,
    Product,
    ProductImage,
    QrScan,
)
from app.products.service import get_product
from app.schemas.passport import (
    PassportSummary,
    PublicCertification,
    PublicDocument,
    PublicImage,
    PublicMaterial,
    PublicPassportResponse,
    PublicProduct,
    PublicSustainability,
    PublishResponse,
)

logger = logging.getLogger("app.passport")


def _frontend_passport_url(
    settings: Settings,
    public_uuid: UUID,
    *,
    from_qr: bool = False,
) -> str:
    base = settings.frontend_url.rstrip("/")
    url = f"{base}/passport/{public_uuid}"
    if from_qr:
        return f"{url}?src=qr"
    return url


def _api_qr_url(settings: Settings, product_id: UUID) -> str:
    prefix = settings.api_prefix.rstrip("/")
    return f"{prefix}/products/{product_id}/passport/qr"


def _api_public_file(
    settings: Settings, public_uuid: UUID, kind: str, item_id: UUID
) -> str:
    prefix = settings.api_prefix.rstrip("/")
    return f"{prefix}/passport/{public_uuid}/{kind}/{item_id}/file"


def _to_summary(
    passport: Passport, *, settings: Settings
) -> PassportSummary:
    return PassportSummary(
        id=passport.id,
        public_uuid=passport.public_uuid,
        version=passport.version,
        status=passport.status,
        verification_status=passport.verification_status,
        public_url=_frontend_passport_url(settings, passport.public_uuid),
        qr_code_url=_api_qr_url(settings, passport.product_id),
        created_at=passport.created_at,
    )


def get_active_passport_for_product(db: Session, product_id: UUID) -> Passport | None:
    return db.scalar(
        select(Passport).where(
            Passport.product_id == product_id,
            Passport.status == PassportStatus.ACTIVE,
        )
    )


# Back-compat alias used by seeds / older call sites.
get_passport_for_product = get_active_passport_for_product


def list_passport_versions(db: Session, product_id: UUID) -> list[Passport]:
    get_product(db, product_id)
    return list(
        db.scalars(
            select(Passport)
            .where(Passport.product_id == product_id)
            .order_by(Passport.version.desc())
        ).all()
    )


def publish_product(
    db: Session,
    product_id: UUID,
    *,
    settings: Settings,
    storage: Storage,
    actor_id: UUID | None = None,
) -> PublishResponse:
    product = get_product(db, product_id)
    active = get_active_passport_for_product(db, product_id)

    if active is None:
        public_uuid = uuid.uuid4()
        version = 1
        qr_target = _frontend_passport_url(settings, public_uuid, from_qr=True)
        qr_key = storage.save_bytes(
            product_id=product.id,
            folder="qr",
            suffix=".png",
            data=make_qr_png(qr_target),
        )
    else:
        # Republish: keep public_uuid (QR stays valid) and bump version.
        public_uuid = active.public_uuid
        version = active.version + 1
        qr_key = active.qr_code_path
        active.status = PassportStatus.REVOKED

    passport = Passport(
        product_id=product.id,
        public_uuid=public_uuid,
        qr_code_path=qr_key,
        version=version,
        status=PassportStatus.ACTIVE,
        verification_status=VerificationStatus.VERIFIED,
    )
    product.status = ProductStatus.PUBLISHED
    db.add(passport)
    audit_service.record(
        db,
        actor_user_id=actor_id,
        action="product.publish" if version == 1 else "product.republish",
        entity_type="product",
        entity_id=product.id,
        details={
            "public_uuid": str(public_uuid),
            "sku": product.sku,
            "version": version,
        },
    )
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        if version == 1:
            storage.delete(qr_key)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product already published",
        ) from None
    db.refresh(passport)
    invalidate_stats_cache()

    logger.info(
        "published product_id=%s public_uuid=%s version=%s",
        product.id,
        passport.public_uuid,
        passport.version,
    )
    return PublishResponse(
        product_id=product.id,
        status=product.status,
        passport=_to_summary(passport, settings=settings),
    )


def _passport_options():
    return (
        joinedload(Passport.product).options(
            selectinload(Product.materials),
            selectinload(Product.sustainability),
            selectinload(Product.certifications).options(
                joinedload(Certification.certification_type),
                joinedload(Certification.issuing_authority),
            ),
            selectinload(Product.documents),
            selectinload(Product.images),
        ),
    )


def _load_passport(
    db: Session,
    public_uuid: UUID,
    *,
    version: int | None = None,
) -> Passport:
    stmt = (
        select(Passport)
        .where(Passport.public_uuid == public_uuid)
        .options(*_passport_options())
    )
    if version is not None:
        stmt = stmt.where(Passport.version == version)
    else:
        stmt = stmt.where(Passport.status == PassportStatus.ACTIVE)

    result = db.execute(stmt)
    passport = result.unique().scalar_one_or_none()
    if passport is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Passport not found",
        )
    if (
        passport.product.status != ProductStatus.PUBLISHED
        or passport.product.deleted_at is not None
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Passport not found",
        )
    return passport


def _to_public_response(
    passport: Passport, *, settings: Settings
) -> PublicPassportResponse:
    product = passport.product
    public_uuid = passport.public_uuid

    materials = [
        PublicMaterial.model_validate(m)
        for m in sorted(product.materials, key=lambda m: m.name)
    ]
    sustainability = (
        PublicSustainability.model_validate(product.sustainability)
        if product.sustainability is not None
        else None
    )
    certifications = [
        PublicCertification(
            name=c.certification_type.name,
            issuing_authority=c.issuing_authority.name,
            issue_date=c.issue_date,
            expiration_date=c.expiration_date,
            pdf_url=_api_public_file(
                settings, public_uuid, "certifications", c.id
            ),
        )
        for c in sorted(
            product.certifications, key=lambda c: c.issue_date, reverse=True
        )
    ]
    documents = [
        PublicDocument(
            doc_type=d.doc_type,
            original_filename=d.original_filename,
            file_url=_api_public_file(settings, public_uuid, "documents", d.id),
        )
        for d in sorted(product.documents, key=lambda d: d.doc_type.value)
    ]
    images = [
        PublicImage(
            id=img.id,
            image_type=img.image_type,
            sort_order=img.sort_order,
            file_url=_api_public_file(settings, public_uuid, "images", img.id),
        )
        for img in sorted(
            product.images, key=lambda img: (img.sort_order, str(img.id))
        )
    ]

    return PublicPassportResponse(
        public_uuid=passport.public_uuid,
        version=passport.version,
        status=passport.status,
        verification_status=passport.verification_status,
        created_at=passport.created_at,
        product=PublicProduct(
            name=product.name,
            sku=product.sku,
            serial_number=product.serial_number,
            category=product.category,
            description=product.description,
            production_date=product.production_date,
            country_of_origin=product.country_of_origin,
        ),
        materials=materials,
        sustainability=sustainability,
        certifications=certifications,
        documents=documents,
        images=images,
    )


def get_public_passport(
    db: Session,
    public_uuid: UUID,
    *,
    settings: Settings,
    version: int | None = None,
) -> PublicPassportResponse:
    passport = _load_passport(db, public_uuid, version=version)
    return _to_public_response(passport, settings=settings)


def _parse_ua(user_agent: str) -> tuple[str, str]:
    ua = user_agent or ""
    browser = "Unknown"
    os_name = "Unknown"
    lower = ua.lower()
    if "edg/" in lower:
        browser = "Edge"
    elif "chrome/" in lower and "chromium" not in lower:
        browser = "Chrome"
    elif "firefox/" in lower:
        browser = "Firefox"
    elif "safari/" in lower and "chrome/" not in lower:
        browser = "Safari"

    if "windows" in lower:
        os_name = "Windows"
    elif "android" in lower:
        os_name = "Android"
    elif "iphone" in lower or "ipad" in lower:
        os_name = "iOS"
    elif "mac os" in lower or "macintosh" in lower:
        os_name = "macOS"
    elif "linux" in lower:
        os_name = "Linux"

    return browser[:100], os_name[:100]


def _lang_code(accept_language: str | None) -> str:
    if not accept_language:
        return "en"
    primary = accept_language.split(",")[0].strip()
    primary = primary.split(";")[0].strip()
    return primary[:20] or "en"


def record_scan(db: Session, passport: Passport, request: Request) -> None:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        ip = forwarded.split(",")[0].strip()
    else:
        ip = request.client.host if request.client else "0.0.0.0"

    browser, os_name = _parse_ua(request.headers.get("user-agent", ""))
    lang = _lang_code(request.headers.get("accept-language"))
    # Mock geo: derive a plausible ISO code from language when possible.
    country = "XX"
    match = re.match(r"^[a-zA-Z]{2}(?:-([A-Z]{2}))?", lang)
    if match and match.group(1):
        country = match.group(1)
    elif lang.lower().startswith("de"):
        country = "DE"
    elif lang.lower().startswith("fr"):
        country = "FR"
    elif lang.lower().startswith("en"):
        country = "US"

    db.add(
        QrScan(
            passport_id=passport.id,
            ip_address=ip[:45],
            browser=browser,
            operating_system=os_name,
            browser_language=lang,
            country=country,
        )
    )


def get_public_passport_and_track(
    db: Session,
    public_uuid: UUID,
    *,
    settings: Settings,
    request: Request,
    src: str | None = None,
    version: int | None = None,
) -> PublicPassportResponse:
    passport = _load_passport(db, public_uuid, version=version)
    payload = _to_public_response(passport, settings=settings)
    # Only QR deep links (?src=qr) count as scans; direct opens do not.
    if src == "qr" and passport.status == PassportStatus.ACTIVE:
        record_scan(db, passport, request)
        db.commit()
        invalidate_stats_cache()
    return payload


def resolve_public_cert_file(
    db: Session, public_uuid: UUID, certification_id: UUID
) -> Certification:
    passport = _load_passport(db, public_uuid)
    cert = next(
        (c for c in passport.product.certifications if c.id == certification_id),
        None,
    )
    if cert is None:
        raise HTTPException(status_code=404, detail="Certification not found")
    return cert


def resolve_public_document(
    db: Session, public_uuid: UUID, document_id: UUID
) -> Document:
    passport = _load_passport(db, public_uuid)
    doc = next((d for d in passport.product.documents if d.id == document_id), None)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


def resolve_public_image(
    db: Session, public_uuid: UUID, image_id: UUID
) -> ProductImage:
    passport = _load_passport(db, public_uuid)
    image = next((i for i in passport.product.images if i.id == image_id), None)
    if image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    return image


def get_or_build_passport_pdf(
    db: Session,
    public_uuid: UUID,
    *,
    settings: Settings,
    storage: Storage,
    version: int | None = None,
) -> tuple[bytes, str]:
    """Return PDF bytes and download filename (uses cache when present)."""
    passport = _load_passport(db, public_uuid, version=version)
    filename = f"passport-{public_uuid}-v{passport.version}.pdf"
    if passport.pdf_path and storage.exists(passport.pdf_path):
        return storage.read_bytes(passport.pdf_path), filename

    payload = _to_public_response(passport, settings=settings)
    pdf_bytes = build_passport_pdf(payload)
    key = storage.save_bytes(
        product_id=passport.product_id,
        folder="passport-pdf",
        suffix=".pdf",
        data=pdf_bytes,
    )
    old = passport.pdf_path
    passport.pdf_path = key
    db.commit()
    if old:
        storage.delete(old)
    return pdf_bytes, filename


def cache_passport_pdf_task(public_uuid: UUID, version: int) -> None:
    """BackgroundTasks entrypoint: build and store PDF after publish."""
    db = SessionLocal()
    try:
        settings = get_settings()
        storage = get_storage()
        get_or_build_passport_pdf(
            db,
            public_uuid,
            settings=settings,
            storage=storage,
            version=version,
        )
        logger.info("cached passport pdf public_uuid=%s version=%s", public_uuid, version)
    except Exception:
        logger.exception(
            "failed to cache passport pdf public_uuid=%s version=%s",
            public_uuid,
            version,
        )
    finally:
        db.close()
