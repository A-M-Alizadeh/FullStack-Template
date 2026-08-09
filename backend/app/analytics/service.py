"""Analytics aggregates from qr_scans."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.products.models import Passport, Product, QrScan
from app.schemas.analytics import AnalyticsResponse, LatestScan, ProductScanStat

TOP_PRODUCTS = 5
LATEST_SCANS = 20


def _start_of_today_utc() -> datetime:
    now = datetime.now(UTC)
    return now.replace(hour=0, minute=0, second=0, microsecond=0)


def get_analytics(db: Session) -> AnalyticsResponse:
    today_start = _start_of_today_utc()
    week_start = today_start - timedelta(days=6)

    scans_today = (
        db.scalar(
            select(func.count())
            .select_from(QrScan)
            .where(QrScan.scanned_at >= today_start)
        )
        or 0
    )
    scans_this_week = (
        db.scalar(
            select(func.count())
            .select_from(QrScan)
            .where(QrScan.scanned_at >= week_start)
        )
        or 0
    )

    top_rows = db.execute(
        select(
            Product.id,
            Product.name,
            Product.sku,
            func.count(QrScan.id).label("scan_count"),
        )
        .join(Passport, Passport.product_id == Product.id)
        .join(QrScan, QrScan.passport_id == Passport.id)
        .where(Product.deleted_at.is_(None))
        .group_by(Product.id, Product.name, Product.sku)
        .order_by(func.count(QrScan.id).desc(), Product.name)
        .limit(TOP_PRODUCTS)
    ).all()

    most_viewed = [
        ProductScanStat(
            product_id=row.id,
            name=row.name,
            sku=row.sku,
            scan_count=row.scan_count,
        )
        for row in top_rows
    ]

    latest_rows = db.execute(
        select(
            QrScan.scanned_at,
            Product.id,
            Product.name,
            Product.sku,
            QrScan.country,
            QrScan.browser,
            QrScan.operating_system,
        )
        .join(Passport, Passport.id == QrScan.passport_id)
        .join(Product, Product.id == Passport.product_id)
        .where(Product.deleted_at.is_(None))
        .order_by(QrScan.scanned_at.desc())
        .limit(LATEST_SCANS)
    ).all()

    latest = [
        LatestScan(
            scanned_at=row.scanned_at,
            product_id=row.id,
            product_name=row.name,
            sku=row.sku,
            country=row.country,
            browser=row.browser,
            operating_system=row.operating_system,
        )
        for row in latest_rows
    ]

    return AnalyticsResponse(
        scans_today=scans_today,
        scans_this_week=scans_this_week,
        most_viewed_products=most_viewed,
        latest_scans=latest,
    )
