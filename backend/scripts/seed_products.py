"""Seed one demo product with nested data (dev only).

Run after users + lookups:
  APP_ENV=local uv run python -m scripts.seed_users
  APP_ENV=local uv run python -m scripts.seed_lookups
  APP_ENV=local uv run python -m scripts.seed_products
"""

from __future__ import annotations

import logging
from datetime import date
from decimal import Decimal

from sqlalchemy import select

import app.database.load_models  # noqa: F401
from app.core.enums import DocumentType, ImageType, ProductCategory, ProductStatus
from app.core.storage import get_storage
from app.database.session import SessionLocal
from app.products.models import (
    Certification,
    CertificationType,
    Document,
    IssuingAuthority,
    Material,
    Product,
    ProductImage,
    Sustainability,
)
from app.users.models import User

logger = logging.getLogger("app.seed")

DEMO_SKU = "DEMO-001"
MINI_PDF = b"%PDF-1.4\n% demo seed\n"


def seed_products() -> None:
    db = SessionLocal()
    storage = get_storage()
    try:
        user = db.scalar(select(User).order_by(User.created_at).limit(1))
        if user is None:
            raise SystemExit("No users found. Run scripts.seed_users first.")

        product = db.scalar(select(Product).where(Product.sku == DEMO_SKU))
        if product is None:
            product = Product(
                created_by_id=user.id,
                name="Demo Wireless Headphones",
                sku=DEMO_SKU,
                serial_number="SN-DEMO-001",
                category=ProductCategory.ELECTRONICS,
                description="Seed product for local API and UI checks.",
                production_date=date(2024, 6, 1),
                country_of_origin="DE",
                status=ProductStatus.DRAFT,
            )
            db.add(product)
            db.flush()
            logger.info("created product %s", DEMO_SKU)
        else:
            logger.info("skip existing product %s", DEMO_SKU)

        if not db.scalars(
            select(Material).where(Material.product_id == product.id)
        ).first():
            db.add_all(
                [
                    Material(
                        product_id=product.id,
                        name="Recycled plastic",
                        percentage=Decimal("55.00"),
                        country_of_origin="DE",
                        recyclable=True,
                    ),
                    Material(
                        product_id=product.id,
                        name="Aluminum",
                        percentage=Decimal("30.00"),
                        country_of_origin="SE",
                        recyclable=True,
                    ),
                    Material(
                        product_id=product.id,
                        name="Other",
                        percentage=Decimal("15.00"),
                        country_of_origin="CN",
                        recyclable=False,
                    ),
                ]
            )
            logger.info("added materials")

        sust = db.scalar(
            select(Sustainability).where(Sustainability.product_id == product.id)
        )
        if sust is None:
            db.add(
                Sustainability(
                    product_id=product.id,
                    carbon_footprint="8.2 kg CO2e",
                    water_consumption="12 L",
                    recycled_material_percent=Decimal("55.00"),
                    repairability_score=Decimal("7.50"),
                    recyclable=True,
                )
            )
            logger.info("added sustainability")

        cert_type = db.scalar(
            select(CertificationType).where(CertificationType.code == "ce")
        )
        authority = db.scalar(
            select(IssuingAuthority).where(IssuingAuthority.code == "tuv")
        )
        if cert_type is None or authority is None:
            raise SystemExit("Lookups missing. Run scripts.seed_lookups first.")

        has_cert = db.scalar(
            select(Certification).where(Certification.product_id == product.id)
        )
        if has_cert is None:
            pdf_key = storage.save_bytes(
                product_id=product.id,
                folder="certs",
                suffix=".pdf",
                data=MINI_PDF,
            )
            db.add(
                Certification(
                    product_id=product.id,
                    certification_type_id=cert_type.id,
                    issuing_authority_id=authority.id,
                    issue_date=date(2024, 1, 15),
                    expiration_date=date(2027, 1, 15),
                    pdf_path=pdf_key,
                )
            )
            logger.info("added certification")

        has_doc = db.scalar(select(Document).where(Document.product_id == product.id))
        if has_doc is None:
            doc_key = storage.save_bytes(
                product_id=product.id,
                folder="docs",
                suffix=".pdf",
                data=MINI_PDF,
            )
            db.add(
                Document(
                    product_id=product.id,
                    doc_type=DocumentType.USER_MANUAL,
                    file_path=doc_key,
                    original_filename="user-manual.pdf",
                )
            )
            logger.info("added document")

        has_cover = db.scalar(
            select(ProductImage).where(
                ProductImage.product_id == product.id,
                ProductImage.image_type == ImageType.COVER,
            )
        )
        if has_cover is None:
            img_key = storage.save_bytes(
                product_id=product.id,
                folder="images",
                suffix=".png",
                data=b"\x89PNG\r\n\x1a\n" + b"\x00" * 32,
            )
            db.add(
                ProductImage(
                    product_id=product.id,
                    image_type=ImageType.COVER,
                    file_path=img_key,
                    sort_order=0,
                )
            )
            logger.info("added cover image")

        db.commit()
        logger.info("demo product id=%s sku=%s", product.id, product.sku)
    finally:
        db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seed_products()
    print("seed products done")
