"""Dashboard aggregates."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.products.models import Passport, Product, QrScan
from app.schemas.dashboard import DashboardResponse


def get_dashboard(db: Session) -> DashboardResponse:
    total_products = db.scalar(select(func.count()).select_from(Product)) or 0
    published_passports = db.scalar(select(func.count()).select_from(Passport)) or 0
    # One QR file is created per passport.
    generated_qr_codes = published_passports
    # Passport views = recorded QR opens (GET /passport/{uuid}?src=qr).
    total_passport_views = db.scalar(select(func.count()).select_from(QrScan)) or 0

    return DashboardResponse(
        total_products=total_products,
        published_passports=published_passports,
        generated_qr_codes=generated_qr_codes,
        total_passport_views=total_passport_views,
    )
