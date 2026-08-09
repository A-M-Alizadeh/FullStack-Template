"""Seed sample audit_logs when the table is empty (dev only).

Run after users + products (+ scans if you want publish/republish context):
  APP_ENV=local uv run python -m scripts.seed_audit
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import func, select

import app.database.load_models  # noqa: F401
from app.audit.models import AuditLog
from app.database.session import SessionLocal
from app.products.models import Passport, Product
from app.users.models import User
from scripts.seed_products import DEMO_SKU

logger = logging.getLogger("app.seed")

TARGET_ROWS = 6


def seed_audit() -> None:
    db = SessionLocal()
    try:
        existing = db.scalar(select(func.count()).select_from(AuditLog)) or 0
        if existing >= TARGET_ROWS:
            logger.info("skip audit seed; already have %s rows", existing)
            return

        admin = db.scalar(
            select(User).where(User.email == "admin@example.com")
        ) or db.scalar(select(User).order_by(User.created_at).limit(1))
        if admin is None:
            raise SystemExit("No users found. Run scripts.seed_users first.")

        product = db.scalar(select(Product).where(Product.sku == DEMO_SKU))
        if product is None:
            raise SystemExit("Demo product missing. Run scripts.seed_products first.")

        passport = db.scalar(
            select(Passport)
            .where(Passport.product_id == product.id)
            .order_by(Passport.version.desc())
            .limit(1)
        )

        now = datetime.now(UTC)
        samples: list[tuple[str, str, UUID | None, dict[str, Any] | None, int]] = [
            (
                "product.create",
                "product",
                product.id,
                {"sku": product.sku, "name": product.name},
                48,
            ),
            (
                "user.create",
                "user",
                admin.id,
                {"email": "editor@example.com", "role": "editor"},
                40,
            ),
            (
                "product.publish",
                "product",
                product.id,
                {
                    "sku": product.sku,
                    "public_uuid": str(passport.public_uuid) if passport else None,
                    "version": 1,
                },
                30,
            ),
            (
                "product.republish",
                "product",
                product.id,
                {
                    "sku": product.sku,
                    "public_uuid": str(passport.public_uuid) if passport else None,
                    "version": passport.version if passport else 2,
                },
                12,
            ),
            (
                "product.delete",
                "product",
                product.id,
                {"sku": product.sku, "name": product.name, "demo": True},
                6,
            ),
            (
                "product.restore",
                "product",
                product.id,
                {"sku": product.sku, "name": product.name, "demo": True},
                5,
            ),
        ]

        need = TARGET_ROWS - int(existing)
        for action, entity_type, entity_id, details, hours_ago in samples[:need]:
            db.add(
                AuditLog(
                    actor_user_id=admin.id,
                    action=action,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    details=details,
                    created_at=now - timedelta(hours=hours_ago),
                )
            )

        db.commit()
        logger.info("added %s audit log rows (target %s)", need, TARGET_ROWS)
    finally:
        db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seed_audit()
    print("seed audit done")
