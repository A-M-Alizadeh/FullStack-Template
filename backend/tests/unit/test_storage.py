"""Unit tests for local file storage."""

from io import BytesIO
from uuid import uuid4

import pytest
from fastapi import UploadFile

from app.core.storage import LocalStorage


def test_save_file_rejects_bad_suffix(tmp_path):
    """Disallowed file extensions raise ValueError."""
    storage = LocalStorage(root=tmp_path, max_upload_bytes=1024 * 1024)
    upload = UploadFile(filename="virus.exe", file=BytesIO(b"x" * 20))
    with pytest.raises(ValueError, match="not allowed"):
        storage.save_file(
            product_id=uuid4(),
            folder="docs",
            upload=upload,
            allowed_suffixes={".pdf"},
        )


def test_save_file_rejects_spoofed_pdf_suffix(tmp_path):
    """Magic bytes must match the declared extension."""
    storage = LocalStorage(root=tmp_path, max_upload_bytes=1024 * 1024)
    upload = UploadFile(filename="fake.pdf", file=BytesIO(b"not-a-pdf-content!!"))
    with pytest.raises(ValueError, match="content does not match"):
        storage.save_file(
            product_id=uuid4(),
            folder="docs",
            upload=upload,
            allowed_suffixes={".pdf"},
        )


def test_save_file_rejects_oversized(tmp_path):
    storage = LocalStorage(root=tmp_path, max_upload_bytes=32)
    upload = UploadFile(filename="big.pdf", file=BytesIO(b"%PDF-1.4\n" + b"x" * 100))
    with pytest.raises(ValueError, match="too large"):
        storage.save_file(
            product_id=uuid4(),
            folder="docs",
            upload=upload,
            allowed_suffixes={".pdf"},
        )


def test_save_bytes_and_path(tmp_path):
    """Saved bytes can be read back via path() / read_bytes()."""
    storage = LocalStorage(root=tmp_path, max_upload_bytes=1024 * 1024)
    key = storage.save_bytes(
        product_id=uuid4(),
        folder="qr",
        suffix=".png",
        data=b"png-bytes",
    )
    assert storage.path(key).read_bytes() == b"png-bytes"
    assert storage.read_bytes(key) == b"png-bytes"
    assert storage.exists(key) is True


def test_path_rejects_traversal(tmp_path):
    storage = LocalStorage(root=tmp_path, max_upload_bytes=1024)
    with pytest.raises(ValueError, match="invalid"):
        storage.path("../secrets.txt")


def test_storage_response_rejects_cross_product_key(tmp_path):
    from app.core.storage import storage_response

    storage = LocalStorage(root=tmp_path, max_upload_bytes=1024)
    pid = uuid4()
    other = uuid4()
    key = storage.save_bytes(
        product_id=pid, folder="docs", suffix=".pdf", data=b"%PDF-1.4\n"
    )
    with pytest.raises(ValueError, match="belong"):
        storage_response(
            storage, key, filename="x.pdf", product_id=other, media_type="application/pdf"
        )
