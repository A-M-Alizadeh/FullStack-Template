"""File storage backend.

Local disk by default. Set STORAGE_BACKEND=minio for MinIO/S3-compatible storage.
"""

from __future__ import annotations

import logging
import uuid
from functools import lru_cache
from pathlib import Path
from typing import Protocol
from urllib.parse import quote

from fastapi import UploadFile
from fastapi.responses import FileResponse, Response

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
        """Absolute path for local downloads (local backend only)."""

    def read_bytes(self, key: str) -> bytes:
        """Read object bytes."""

    def exists(self, key: str) -> bool:
        """True when the object exists."""

    def delete(self, key: str) -> None:
        """Remove object if it exists."""


def storage_response(
    storage: Storage,
    key: str,
    *,
    filename: str,
    media_type: str | None = None,
) -> Response:
    """Serve a stored object as an HTTP response (local path or streamed bytes)."""
    if isinstance(storage, LocalStorage):
        path = storage.path(key)
        return FileResponse(path, filename=filename, media_type=media_type)
    data = storage.read_bytes(key)
    headers = {
        "Content-Disposition": f"attachment; filename*=UTF-8''{quote(filename)}"
    }
    return Response(content=data, media_type=media_type, headers=headers)


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

    def read_bytes(self, key: str) -> bytes:
        return self.path(key).read_bytes()

    def exists(self, key: str) -> bool:
        try:
            return self.path(key).is_file()
        except ValueError:
            return False

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


class MinioStorage:
    """S3-compatible object storage (MinIO)."""

    def __init__(
        self,
        *,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket: str,
        secure: bool,
    ) -> None:
        from minio import Minio

        self.bucket = bucket
        self._client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
        )
        if not self._client.bucket_exists(bucket):
            self._client.make_bucket(bucket)
            logger.info("created minio bucket %s", bucket)

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
        data = upload.file.read()
        key = self._key(product_id, folder, suffix)
        self._put(key, data)
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
        self._put(key, data)
        return key

    def path(self, key: str) -> Path:
        raise NotImplementedError("MinIO storage has no local path; use read_bytes()")

    def read_bytes(self, key: str) -> bytes:
        response = self._client.get_object(self.bucket, key)
        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()

    def exists(self, key: str) -> bool:
        from minio.error import S3Error

        try:
            self._client.stat_object(self.bucket, key)
            return True
        except S3Error:
            return False

    def delete(self, key: str) -> None:
        from minio.error import S3Error

        try:
            self._client.remove_object(self.bucket, key)
            logger.info("deleted object %s", key)
        except S3Error:
            return

    def _put(self, key: str, data: bytes) -> None:
        from io import BytesIO

        self._client.put_object(
            self.bucket,
            key,
            BytesIO(data),
            length=len(data),
        )

    def _key(self, product_id: uuid.UUID, folder: str, suffix: str) -> str:
        return (
            Path("products") / str(product_id) / folder / f"{uuid.uuid4().hex}{suffix}"
        ).as_posix()


def _root_from_settings(settings: Settings) -> Path:
    path = Path(settings.upload_dir)
    if not path.is_absolute():
        path = BASE_DIR / path
    return path


@lru_cache
def get_storage() -> Storage:
    settings = get_settings()
    backend = (settings.storage_backend or "local").strip().lower()
    if backend == "minio":
        return MinioStorage(
            endpoint=settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            bucket=settings.minio_bucket,
            secure=settings.minio_secure,
        )
    return LocalStorage(root=_root_from_settings(settings))


def reset_storage_for_tests() -> None:
    get_storage.cache_clear()
