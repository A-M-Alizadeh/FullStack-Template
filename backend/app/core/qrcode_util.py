"""Build QR code PNG bytes for a URL."""

from __future__ import annotations

from io import BytesIO

import qrcode
from qrcode.constants import ERROR_CORRECT_M


def make_qr_png(url: str) -> bytes:
    qr = qrcode.QRCode(version=None, error_correction=ERROR_CORRECT_M, box_size=8, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    image = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()
