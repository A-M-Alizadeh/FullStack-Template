"""Dashboard aggregates."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.cache import DASHBOARD_KEY, DEFAULT_TTL, get_cache
from app.core.enums import PassportStatus
from app.products.models import Passport, Product, QrScan
from app.schemas.dashboard import DashboardResponse


def get_dashboard(db: Session) -> DashboardResponse:
    cache = get_cache()
    cached = cache.get_json(DASHBOARD_KEY)
    if cached is not None:
        return DashboardResponse.model_validate(cached)

    active = Product.deleted_at.is_(None)
    total_products = (
        db.scalar(select(func.count()).select_from(Product).where(active)) or 0
    )
    published_passports = (
        db.scalar(
            select(func.count())
            .select_from(Passport)
            .join(Product, Product.id == Passport.product_id)
            .where(active, Passport.status == PassportStatus.ACTIVE)
        )
        or 0
    )
    # One QR file is created per product lineage (reused across versions).
    generated_qr_codes = published_passports
    # Passport views = recorded QR opens (GET /passport/{uuid}?src=qr).
    total_passport_views = db.scalar(select(func.count()).select_from(QrScan)) or 0

    payload = DashboardResponse(
        total_products=total_products,
        published_passports=published_passports,
        generated_qr_codes=generated_qr_codes,
        total_passport_views=total_passport_views,
    )
    cache.set_json(DASHBOARD_KEY, payload.model_dump(mode="json"), ttl_seconds=DEFAULT_TTL)
    return payload
