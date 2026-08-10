"""Unit tests for upload magic / size helpers."""

import pytest

from app.core.uploads import assert_storage_key, assert_upload_allowed


def test_assert_upload_pdf_ok():
    assert (
        assert_upload_allowed(
            filename="a.pdf",
            data=b"%PDF-1.4\nhello",
            allowed_suffixes={".pdf"},
            max_bytes=1000,
        )
        == ".pdf"
    )


def test_assert_storage_key_product_bound():
    pid = "11111111-1111-1111-1111-111111111111"
    key = f"products/{pid}/docs/abc.pdf"
    assert assert_storage_key(key, product_id=pid) == key
    with pytest.raises(ValueError):
        assert_storage_key(key, product_id="22222222-2222-2222-2222-222222222222")
    with pytest.raises(ValueError):
        assert_storage_key("../etc/passwd")
