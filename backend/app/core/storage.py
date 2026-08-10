"""File storage backend.

Local disk by default. Set STORAGE_BACKEND=minio for MinIO/S3-compatible storage.

Objects are keyed under products/{product_id}/… — never serve arbitrary paths.
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
from app.core.uploads import assert_storage_key, assert_upload_allowed

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
    product_id: uuid.UUID | None = None,
) -> Response:
    """Serve a stored object after validating the key belongs to the product."""
    safe_key = assert_storage_key(key, product_id=product_id)
    if isinstance(storage, LocalStorage):
        path = storage.path(safe_key)
        return FileResponse(path, filename=filename, media_type=media_type)
    data = storage.read_bytes(safe_key)
    headers = {
        "Content-Disposition": f"attachment; filename*=UTF-8''{quote(filename)}"
    }
    return Response(content=data, media_type=media_type, headers=headers)


def _read_upload_capped(upload: UploadFile, max_bytes: int) -> bytes:
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = upload.file.read(1024 * 1024)
        if not chunk:
            break
        total += len(chunk)
        if total > max_bytes:
            raise ValueError(f"file too large (max {max_bytes} bytes)")
        chunks.append(chunk)
    return b"".join(chunks)


class LocalStorage:
    """Files under UPLOAD_DIR on disk."""

    def __init__(self, root: Path, *, max_upload_bytes: int) -> None:
        self.root = root
        self.max_upload_bytes = max_upload_bytes
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
        data = _read_upload_capped(upload, self.max_upload_bytes)
        suffix = assert_upload_allowed(
            filename=original,
            data=data,
            allowed_suffixes=allowed_suffixes,
            max_bytes=self.max_upload_bytes,
        )
        key = self._key(product_id, folder, suffix)
        absolute = self.path(key)
        absolute.parent.mkdir(parents=True, exist_ok=True)
        absolute.write_bytes(data)
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
        if len(data) > self.max_upload_bytes:
            raise ValueError(f"file too large (max {self.max_upload_bytes} bytes)")
        key = self._key(product_id, folder, suffix.lower())
        absolute = self.path(key)
        absolute.parent.mkdir(parents=True, exist_ok=True)
        absolute.write_bytes(data)
        return key

    def path(self, key: str) -> Path:
        safe = assert_storage_key(key)
        root = self.root.resolve()
        absolute = (root / safe).resolve()
        try:
            absolute.relative_to(root)
        except ValueError as exc:
            raise ValueError("invalid file path") from exc
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
        safe_folder = folder.replace("..", "").strip("/\\") or "files"
        return (
            Path("products")
            / str(product_id)
            / safe_folder
            / f"{uuid.uuid4().hex}{suffix}"
        ).as_posix()


class MinioStorage:
    """S3-compatible object storage (MinIO). App never exposes bucket listing."""

    def __init__(
        self,
        *,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket: str,
        secure: bool,
        max_upload_bytes: int,
    ) -> None:
        from minio import Minio

        self.bucket = bucket
        self.max_upload_bytes = max_upload_bytes
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
        data = _read_upload_capped(upload, self.max_upload_bytes)
        suffix = assert_upload_allowed(
            filename=original,
            data=data,
            allowed_suffixes=allowed_suffixes,
            max_bytes=self.max_upload_bytes,
        )
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
        if len(data) > self.max_upload_bytes:
            raise ValueError(f"file too large (max {self.max_upload_bytes} bytes)")
        key = self._key(product_id, folder, suffix.lower())
        self._put(key, data)
        return key

    def path(self, key: str) -> Path:
        raise NotImplementedError("MinIO storage has no local path; use read_bytes()")

    def read_bytes(self, key: str) -> bytes:
        safe = assert_storage_key(key)
        response = self._client.get_object(self.bucket, safe)
        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()

    def exists(self, key: str) -> bool:
        from minio.error import S3Error

        try:
            self._client.stat_object(self.bucket, assert_storage_key(key))
            return True
        except (S3Error, ValueError):
            return False

    def delete(self, key: str) -> None:
        from minio.error import S3Error

        try:
            self._client.remove_object(self.bucket, assert_storage_key(key))
            logger.info("deleted object %s", key)
        except (S3Error, ValueError):
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
        safe_folder = folder.replace("..", "").strip("/\\") or "files"
        return (
            Path("products")
            / str(product_id)
            / safe_folder
            / f"{uuid.uuid4().hex}{suffix}"
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
            max_upload_bytes=settings.max_upload_bytes,
        )
    return LocalStorage(
        root=_root_from_settings(settings),
        max_upload_bytes=settings.max_upload_bytes,
    )


def reset_storage_for_tests() -> None:
    get_storage.cache_clear()
