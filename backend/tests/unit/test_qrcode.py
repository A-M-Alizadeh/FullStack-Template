"""Unit tests for QR PNG generation."""

from app.core.qrcode_util import make_qr_png


def test_make_qr_png_returns_png_bytes():
    """QR helper returns a non-empty PNG."""
    data = make_qr_png("https://example.com/passport/abc?src=qr")
    assert data.startswith(b"\x89PNG")
    assert len(data) > 100
