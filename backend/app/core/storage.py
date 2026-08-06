"""File storage backend.

Local disk today. To use MinIO/S3 later, add another class with the same
methods and return it from get_storage().
"""

from __future__ import annotations

import logging
import uuid
from functools import lru_cache
from pathlib import Path
from typing import Protocol

from fastapi import UploadFile

from app.core.config import BASE_DIR, Settings, get_settings

logger = logging.getLogger("app.storage")


class Storage(Protocol):
    def save_file(
        self,
        *,
        product_id: uuid.UUID,
        folder: str,
        upload: UploadFile,
        allowed_suffixes: set[str],
    ) -> tuple[str, str]:
        """Store an upload. Returns (storage_key, original_filename)."""

    def save_bytes(
        self,
        *,
        product_id: uuid.UUID,
        folder: str,
        suffix: str,
        data: bytes,
    ) -> str:
        """Store raw bytes. Returns storage_key."""

    def path(self, key: str) -> Path:
        """Absolute path for download (local). Object stores can stream instead later."""

    def delete(self, key: str) -> None:
        """Remove object if it exists."""


class LocalStorage:
    """Files under UPLOAD_DIR on disk."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def save_file(
        self,
        *,
        product_id: uuid.UUID,
        folder: str,
        upload: UploadFile,
        allowed_suffixes: set[str],
    ) -> tuple[str, str]:
        original = (upload.filename or "upload").strip() or "upload"
        suffix = Path(original).suffix.lower()
        if suffix not in allowed_suffixes:
            raise ValueError(f"file type not allowed: {suffix or '(none)'}")

        key = self._key(product_id, folder, suffix)
        absolute = self._absolute(key)
        absolute.parent.mkdir(parents=True, exist_ok=True)

        with absolute.open("wb") as out:
            while True:
                chunk = upload.file.read(1024 * 1024)
                if not chunk:
                    break
                out.write(chunk)

        return key, original

    def save_bytes(
        self,
        *,
        product_id: uuid.UUID,
        folder: str,
        suffix: str,
        data: bytes,
    ) -> str:
        if not suffix.startswith("."):
            suffix = f".{suffix}"
        key = self._key(product_id, folder, suffix.lower())
        absolute = self._absolute(key)
        absolute.parent.mkdir(parents=True, exist_ok=True)
        absolute.write_bytes(data)
        return key

    def path(self, key: str) -> Path:
        root = self.root.resolve()
        absolute = (root / key).resolve()
        if not str(absolute).startswith(str(root)):
            raise ValueError("invalid file path")
        return absolute

    def delete(self, key: str) -> None:
        try:
            absolute = self.path(key)
        except ValueError:
            return
        if absolute.is_file():
            absolute.unlink()
            logger.info("deleted file %s", key)

    def _key(self, product_id: uuid.UUID, folder: str, suffix: str) -> str:
        return (
            Path("products") / str(product_id) / folder / f"{uuid.uuid4().hex}{suffix}"
        ).as_posix()

    def _absolute(self, key: str) -> Path:
        return self.root / key


def _root_from_settings(settings: Settings) -> Path:
    path = Path(settings.upload_dir)
    if not path.is_absolute():
        path = BASE_DIR / path
    return path


@lru_cache
def get_storage() -> LocalStorage:
    return LocalStorage(root=_root_from_settings(get_settings()))
