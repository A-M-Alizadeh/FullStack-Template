"""Bulk-insert products for local load / stress runs (dev only).

Requires users. Does not publish by default (keeps inserts fast).
Use --publish-every N to create passports for a sample.

Examples:
  APP_ENV=local uv run python -m scripts.seed_load --count 1000
  APP_ENV=local uv run python -m scripts.seed_load --count 5000 --batch-size 200
  APP_ENV=local uv run python -m scripts.seed_load --count 200 --publish-every 20
"""

from __future__ import annotations

import argparse
import logging
import time
from datetime import date
from decimal import Decimal

from sqlalchemy import func, select

import app.database.load_models  # noqa: F401
from app.core.config import get_settings
from app.core.enums import ProductCategory, ProductStatus
from app.core.storage import get_storage
from app.database.session import SessionLocal
from app.passport.service import publish_product
from app.products.models import Material, Product, Sustainability
from app.users.models import User

logger = logging.getLogger("app.seed")

SKU_PREFIX = "LOAD-"
CATEGORIES = list(ProductCategory)


def _existing_load_count(db) -> int:
    return int(
        db.scalar(
            select(func.count())
            .select_from(Product)
            .where(Product.sku.like(f"{SKU_PREFIX}%"))
        )
        or 0
    )


def seed_load(
    *,
    count: int,
    batch_size: int,
    publish_every: int,
    start_index: int | None,
) -> None:
    if count < 1:
        raise SystemExit("--count must be >= 1")
    if batch_size < 1:
        raise SystemExit("--batch-size must be >= 1")

    db = SessionLocal()
    settings = get_settings()
    storage = get_storage()
    try:
        user = db.scalar(select(User).order_by(User.created_at).limit(1))
        if user is None:
            raise SystemExit("No users found. Run scripts.seed_users first.")

        if start_index is None:
            start_index = _existing_load_count(db) + 1

        created = 0
        published = 0
        pending_publish: list[Product] = []
        t0 = time.perf_counter()
        batch: list[tuple[int, Product]] = []

        def flush_batch() -> None:
            nonlocal created, published
            if not batch:
                return
            products = [p for _, p in batch]
            db.add_all(products)
            db.flush()
            for idx, product in batch:
                db.add(
                    Material(
                        product_id=product.id,
                        name="Load plastic",
                        percentage=Decimal("60.00"),
                        country_of_origin="DE",
                        recyclable=True,
                    )
                )
                db.add(
                    Sustainability(
                        product_id=product.id,
                        carbon_footprint="12 kg CO2e",
                        water_consumption="80 L",
                        recycled_material_percent=Decimal("40.00"),
                        repairability_score=Decimal("70.00"),
                        recyclable=True,
                    )
                )
                if publish_every > 0 and idx % publish_every == 0:
                    pending_publish.append(product)
            db.commit()
            created += len(batch)
            batch.clear()

            for product in pending_publish:
                publish_product(
                    db,
                    product.id,
                    settings=settings,
                    storage=storage,
                    actor_id=user.id,
                )
                published += 1
            pending_publish.clear()
            logger.info("progress created=%s published=%s", created, published)

        for offset in range(count):
            idx = start_index + offset
            sku = f"{SKU_PREFIX}{idx:05d}"
            exists = db.scalar(select(Product.id).where(Product.sku == sku))
            if exists is not None:
                continue
            product = Product(
                created_by_id=user.id,
                name=f"Load Product {idx}",
                sku=sku,
                serial_number=f"SN-LOAD-{idx:05d}",
                category=CATEGORIES[idx % len(CATEGORIES)],
                description="Bulk-seeded row for load testing.",
                production_date=date(2024, 1, 1),
                country_of_origin="DE",
                status=ProductStatus.DRAFT,
            )
            batch.append((idx, product))
            if len(batch) >= batch_size:
                flush_batch()

        flush_batch()

        elapsed = time.perf_counter() - t0
        total_load = _existing_load_count(db)
        print(
            f"seed_load done: +{created} products "
            f"(publish={published}, total LOAD-*={total_load}, {elapsed:.1f}s)"
        )
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Bulk seed products for load tests.")
    parser.add_argument("--count", type=int, default=1000)
    parser.add_argument("--batch-size", type=int, default=100)
    parser.add_argument(
        "--publish-every",
        type=int,
        default=0,
        help="Publish every Nth SKU index (0 = none)",
    )
    parser.add_argument(
        "--start-index",
        type=int,
        default=None,
        help="SKU index start (default: continue after existing LOAD-* rows)",
    )
    args = parser.parse_args()
    seed_load(
        count=args.count,
        batch_size=args.batch_size,
        publish_every=args.publish_every,
        start_index=args.start_index,
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
