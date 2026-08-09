"""Build a simple Digital Product Passport PDF."""

from __future__ import annotations

from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from app.schemas.passport import PublicPassportResponse


def build_passport_pdf(data: PublicPassportResponse) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 20 * mm

    def line(text: str, *, size: int = 11, gap: int = 6) -> None:
        nonlocal y
        if y < 20 * mm:
            c.showPage()
            y = height - 20 * mm
        c.setFont("Helvetica", size)
        c.drawString(20 * mm, y, text[:110])
        y -= gap * mm

    product = data.product
    line("Digital Product Passport", size=16, gap=10)
    line(product.name, size=14, gap=8)
    line(f"SKU: {product.sku}")
    line(f"Serial: {product.serial_number}")
    line(f"Category: {product.category}")
    line(f"Origin: {product.country_of_origin}")
    line(f"Production date: {product.production_date}")
    line(f"Status: {data.status} / {data.verification_status}")
    line(f"Passport ID: {data.public_uuid}", gap=8)
    line(f"Version: {data.version}")
    line(f"Created: {data.created_at.isoformat()}", gap=10)

    if product.description:
        line("Description", size=12, gap=6)
        for chunk in _wrap(product.description, 90):
            line(chunk, size=10, gap=5)
        y -= 4 * mm

    if data.materials:
        line("Materials", size=12, gap=6)
        for m in data.materials:
            line(
                f"- {m.name}: {m.percentage}% ({m.country_of_origin})"
                f"{' recyclable' if m.recyclable else ''}",
                size=10,
                gap=5,
            )
        y -= 4 * mm

    if data.sustainability:
        s = data.sustainability
        line("Sustainability", size=12, gap=6)
        line(f"- Carbon: {s.carbon_footprint}", size=10, gap=5)
        line(f"- Water: {s.water_consumption}", size=10, gap=5)
        line(f"- Recycled material: {s.recycled_material_percent}%", size=10, gap=5)
        line(f"- Repairability: {s.repairability_score}", size=10, gap=5)
        y -= 4 * mm

    if data.certifications:
        line("Certifications", size=12, gap=6)
        for cert in data.certifications:
            line(
                f"- {cert.name} / {cert.issuing_authority} ({cert.issue_date})",
                size=10,
                gap=5,
            )

    c.showPage()
    c.save()
    return buffer.getvalue()


def _wrap(text: str, width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        if len(trial) <= width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [""]
