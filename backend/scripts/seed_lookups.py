"""Seed certification lookup tables.

Usage (from backend/):
  APP_ENV=local uv run python -m scripts.seed_lookups
"""

from __future__ import annotations

import logging

from sqlalchemy import select

import app.database.load_models  # noqa: F401
from app.database.session import SessionLocal
from app.products.models import CertificationType, IssuingAuthority

logger = logging.getLogger("app.seed")

AUTHORITIES = (
    ("tuv", "TÜV"),
    ("sgs", "SGS"),
    ("ul", "UL"),
    ("bv", "Bureau Veritas"),
)

CERT_TYPES = (
    ("iso_9001", "ISO 9001"),
    ("iso_14001", "ISO 14001"),
    ("ce", "CE Marking"),
    ("rohs", "RoHS"),
)


def seed_lookups() -> None:
    db = SessionLocal()
    try:
        for code, name in AUTHORITIES:
            exists = db.scalar(
                select(IssuingAuthority).where(IssuingAuthority.code == code)
            )
            if exists is not None:
                logger.info("skip authority %s", code)
                continue
            db.add(IssuingAuthority(code=code, name=name))
            logger.info("created authority %s", code)

        for code, name in CERT_TYPES:
            exists = db.scalar(
                select(CertificationType).where(CertificationType.code == code)
            )
            if exists is not None:
                logger.info("skip cert type %s", code)
                continue
            db.add(CertificationType(code=code, name=name))
            logger.info("created cert type %s", code)

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seed_lookups()
    print("seed lookups done")
