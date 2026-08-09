"""Unit tests for passport PDF builder."""

from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import uuid4

from app.core.enums import (
    PassportStatus,
    ProductCategory,
    VerificationStatus,
)
from app.passport.pdf import build_passport_pdf
from app.schemas.passport import (
    PublicMaterial,
    PublicPassportResponse,
    PublicProduct,
)


def test_build_passport_pdf_returns_pdf_bytes():
    data = PublicPassportResponse(
        public_uuid=uuid4(),
        version=2,
        status=PassportStatus.ACTIVE,
        verification_status=VerificationStatus.VERIFIED,
        created_at=datetime.now(UTC),
        product=PublicProduct(
            name="Headphones",
            sku="SKU-1",
            serial_number="SN-1",
            category=ProductCategory.ELECTRONICS,
            description="A demo product with enough text to wrap.",
            production_date=date(2024, 1, 15),
            country_of_origin="DE",
        ),
        materials=[
            PublicMaterial(
                name="Plastic",
                percentage=Decimal("80.00"),
                country_of_origin="DE",
                recyclable=True,
            )
        ],
        sustainability=None,
        certifications=[],
        documents=[],
        images=[],
    )
    pdf = build_passport_pdf(data)
    assert pdf.startswith(b"%PDF")
    assert len(pdf) > 200
