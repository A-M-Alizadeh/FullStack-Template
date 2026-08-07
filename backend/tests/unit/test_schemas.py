"""Unit tests for request schema validation."""

import pytest
from pydantic import ValidationError

from app.schemas.common import normalize_country_code
from app.schemas.products import ProductCreate


def test_normalize_country_code_ok():
    """Valid ISO-2 codes are uppercased."""
    assert normalize_country_code("de") == "DE"


def test_normalize_country_code_rejects_short():
    """Single-letter country codes are rejected."""
    with pytest.raises(ValueError, match="2-letter"):
        normalize_country_code("D")


def test_normalize_country_code_rejects_long():
    """Three-letter country codes are rejected."""
    with pytest.raises(ValueError, match="2-letter"):
        normalize_country_code("DEU")


def test_product_create_rejects_empty_name():
    """Whitespace-only name fails validation."""
    with pytest.raises(ValidationError):
        ProductCreate(
            name="   ",
            sku="SKU-1",
            serial_number="SN-1",
            category="electronics",
            production_date="2024-01-01",
            country_of_origin="DE",
        )


def test_product_create_rejects_bad_category():
    """Unknown category enum fails validation."""
    with pytest.raises(ValidationError):
        ProductCreate(
            name="Item",
            sku="SKU-1",
            serial_number="SN-1",
            category="not-a-category",
            production_date="2024-01-01",
            country_of_origin="DE",
        )


def test_product_create_rejects_bad_country():
    """Invalid country on product create fails validation."""
    with pytest.raises(ValidationError):
        ProductCreate(
            name="Item",
            sku="SKU-1",
            serial_number="SN-1",
            category="electronics",
            production_date="2024-01-01",
            country_of_origin="D",
        )
