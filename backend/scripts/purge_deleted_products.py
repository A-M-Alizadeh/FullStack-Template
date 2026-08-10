"""Hard-delete soft-deleted products older than the retention window.

Default retention: SOFT_DELETE_RETENTION_DAYS (30).

Examples:
  APP_ENV=local uv run python -m scripts.purge_deleted_products --dry-run
  APP_ENV=local uv run python -m scripts.purge_deleted_products --days 30
  APP_ENV=local uv run python -m scripts.purge_deleted_products --days 1
"""

from __future__ import annotations

import argparse
import logging

import app.database.load_models  # noqa: F401
from app.core.config import get_settings
from app.core.storage import get_storage
from app.database.session import SessionLocal
from app.products import service as products_service

logger = logging.getLogger("app.purge")


def main() -> None:
    settings = get_settings()
    parser = argparse.ArgumentParser(
        description="Purge soft-deleted products past retention."
    )
    parser.add_argument(
        "--days",
        type=int,
        default=settings.soft_delete_retention_days,
        help="Purge rows with deleted_at older than this many days",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List candidates without deleting",
    )
    args = parser.parse_args()

    db = SessionLocal()
    storage = get_storage()
    try:
        purged = products_service.purge_soft_deleted_products(
            db,
            storage=storage,
            older_than_days=args.days,
            dry_run=args.dry_run,
        )
        mode = "dry-run" if args.dry_run else "purged"
        print(f"{mode}: {len(purged)} product(s) (retention={args.days}d)")
        for product_id in purged:
            print(f"  - {product_id}")
    finally:
        db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
