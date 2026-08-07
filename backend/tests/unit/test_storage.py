"""Unit tests for local file storage."""

from io import BytesIO
from uuid import uuid4

import pytest
from fastapi import UploadFile

from app.core.storage import LocalStorage


def test_save_file_rejects_bad_suffix(tmp_path):
    """Disallowed file extensions raise ValueError."""
    storage = LocalStorage(root=tmp_path)
    upload = UploadFile(filename="virus.exe", file=BytesIO(b"x"))
    with pytest.raises(ValueError, match="not allowed"):
        storage.save_file(
            product_id=uuid4(),
            folder="docs",
            upload=upload,
            allowed_suffixes={".pdf"},
        )


def test_save_bytes_and_path(tmp_path):
    """Saved bytes can be read back via path()."""
    storage = LocalStorage(root=tmp_path)
    key = storage.save_bytes(
        product_id=uuid4(),
        folder="qr",
        suffix=".png",
        data=b"png-bytes",
    )
    assert storage.path(key).read_bytes() == b"png-bytes"
