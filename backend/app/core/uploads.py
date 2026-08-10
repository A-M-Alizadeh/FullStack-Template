"""Upload size and magic-byte checks (suffix alone is not enough)."""

from __future__ import annotations

from pathlib import Path

# Suffix → accepted magic prefixes (first bytes of file).
_MAGIC: dict[str, tuple[bytes, ...]] = {
    ".pdf": (b"%PDF",),
    ".png": (b"\x89PNG\r\n\x1a\n",),
    ".jpg": (b"\xff\xd8\xff",),
    ".jpeg": (b"\xff\xd8\xff",),
    ".webp": (b"RIFF",),  # full check also needs WEBP at offset 8
}


def normalize_suffix(filename: str) -> str:
    return Path(filename or "").suffix.lower()


def assert_upload_allowed(
    *,
    filename: str,
    data: bytes,
    allowed_suffixes: set[str],
    max_bytes: int,
) -> str:
    """Validate size + magic bytes. Returns normalized suffix or raises ValueError."""
    if max_bytes < 1:
        raise ValueError("invalid max upload size")
    if len(data) == 0:
        raise ValueError("empty file")
    if len(data) > max_bytes:
        raise ValueError(f"file too large (max {max_bytes} bytes)")

    suffix = normalize_suffix(filename)
    if suffix not in allowed_suffixes:
        raise ValueError(f"file type not allowed: {suffix or '(none)'}")

    magics = _MAGIC.get(suffix)
    if magics is None:
        raise ValueError(f"file type not allowed: {suffix}")

    if suffix == ".webp":
        if not (data.startswith(b"RIFF") and len(data) >= 12 and data[8:12] == b"WEBP"):
            raise ValueError("file content does not match extension")
    elif not any(data.startswith(magic) for magic in magics):
        raise ValueError("file content does not match extension")

    return suffix


def assert_storage_key(key: str, *, product_id: object | None = None) -> str:
    """Reject path traversal and optional cross-product keys."""
    cleaned = (key or "").replace("\\", "/").lstrip("/")
    if not cleaned or cleaned.startswith("/") or ".." in cleaned.split("/"):
        raise ValueError("invalid storage key")
    if product_id is not None:
        prefix = f"products/{product_id}/"
        if not cleaned.startswith(prefix):
            raise ValueError("storage key does not belong to product")
    return cleaned
