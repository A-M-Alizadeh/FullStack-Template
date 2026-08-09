"""Seed demo QR scans, passport versions, and PDF cache (dev only).

Publishes DEMO-001 if needed, republishes once for version history, caches PDF,
then adds sample qr_scans.

Run after products:
  APP_ENV=local uv run python -m scripts.seed_users
  APP_ENV=local uv run python -m scripts.seed_lookups
  APP_ENV=local uv run python -m scripts.seed_products
  APP_ENV=local uv run python -m scripts.seed_scans
  APP_ENV=local uv run python -m scripts.seed_audit
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select

import app.database.load_models  # noqa: F401
from app.core.config import get_settings
from app.core.storage import get_storage
from app.database.session import SessionLocal
from app.passport.service import (
    get_active_passport_for_product,
    get_or_build_passport_pdf,
    list_passport_versions,
    publish_product,
)
from app.products.models import Passport, Product, QrScan
from scripts.seed_products import DEMO_SKU

logger = logging.getLogger("app.seed")

# Keep a small fixed sample set; re-runs only fill up to this count.
TARGET_SCANS = 8

SAMPLE_SCANS = (
    # (days_ago, hour_utc, country, browser, os, lang)
    (0, 9, "DE", "Chrome", "Android", "de-DE"),
    (0, 14, "US", "Safari", "iOS", "en-US"),
    (1, 11, "FR", "Firefox", "Windows", "fr-FR"),
    (2, 16, "DE", "Chrome", "macOS", "de-DE"),
    (3, 10, "GB", "Edge", "Windows", "en-GB"),
    (4, 18, "US", "Chrome", "Android", "en-US"),
    (5, 8, "NL", "Safari", "iOS", "nl-NL"),
    (6, 20, "DE", "Chrome", "Linux", "de-DE"),
)


def seed_scans() -> None:
    db = SessionLocal()
    settings = get_settings()
    storage = get_storage()
    try:
        product = db.scalar(select(Product).where(Product.sku == DEMO_SKU))
        if product is None:
            raise SystemExit("Demo product missing. Run scripts.seed_products first.")

        versions = list_passport_versions(db, product.id)
        if not versions:
            logger.info("publishing %s for scan seed", DEMO_SKU)
            publish_product(db, product.id, settings=settings, storage=storage)
            versions = list_passport_versions(db, product.id)

        if len(versions) < 2:
            logger.info("republishing %s for version history seed", DEMO_SKU)
            publish_product(db, product.id, settings=settings, storage=storage)

        passport = get_active_passport_for_product(db, product.id)
        if passport is None:
            raise SystemExit("Publish failed; no active passport.")

        # Ensure PDF exists for the public download button.
        get_or_build_passport_pdf(
            db,
            passport.public_uuid,
            settings=settings,
            storage=storage,
            version=passport.version,
        )
        logger.info(
            "passport ready sku=%s public_uuid=%s version=%s",
            DEMO_SKU,
            passport.public_uuid,
            passport.version,
        )

        passport_ids = list(
            db.scalars(
                select(Passport.id).where(Passport.product_id == product.id)
            ).all()
        )
        existing = (
            db.scalar(
                select(func.count())
                .select_from(QrScan)
                .where(QrScan.passport_id.in_(passport_ids))
            )
            or 0
        )
        if existing >= TARGET_SCANS:
            logger.info(
                "skip scans product_id=%s already has %s rows",
                product.id,
                existing,
            )
            return

        now = datetime.now(UTC)
        need = TARGET_SCANS - existing
        to_add = SAMPLE_SCANS[:need]
        for days_ago, hour, country, browser, os_name, lang in to_add:
            scanned_at = (now - timedelta(days=days_ago)).replace(
                hour=hour, minute=15, second=0, microsecond=0
            )
            db.add(
                QrScan(
                    passport_id=passport.id,
                    scanned_at=scanned_at,
                    ip_address="127.0.0.1",
                    browser=browser,
                    operating_system=os_name,
                    browser_language=lang,
                    country=country,
                )
            )
        db.commit()
        logger.info(
            "added %s scans for %s (total target %s)",
            len(to_add),
            DEMO_SKU,
            TARGET_SCANS,
        )
    finally:
        db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seed_scans()
    print("seed scans done")
