"""Generate docs/DPP_Project_Overview.pdf from the project report summary.

  APP_ENV=local uv run python -m scripts.generate_overview_pdf
"""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUT_PATH = PROJECT_ROOT / "docs" / "DPP_Project_Overview.pdf"

SECTIONS: list[tuple[str, list[str]]] = [
    (
        "Digital Product Passport — Overview",
        [
            "Full-stack DPP: back office → publish → QR → public passport + scans.",
            "Stack: FastAPI + Postgres + Alembic · Next.js + MUI + RTK Query.",
            "Full write-up: docs/REPORT.md (architecture, security, load, demo).",
        ],
    ),
    (
        "Run locally",
        [
            "1. Copy env examples; docker compose up db",
            "2. backend: uv sync, alembic upgrade head, seed_*, uvicorn",
            "3. frontend: npm i && npm run dev",
            "4. App :3000 · API docs :8000/docs",
            "Logins: admin@example.com / admin1234 · editor@example.com / editor1234",
        ],
    ),
    (
        "Architecture choices",
        [
            "Separate passports table with stable public_uuid (QR-safe).",
            "Republish bumps version, keeps UUID; soft delete + retention purge.",
            "Shared editor workspace; roles admin|editor; Storage protocol local/MinIO.",
            "Prod API: Gunicorn + Uvicorn workers; optional Redis cache.",
        ],
    ),
    (
        "Security highlights",
        [
            "JWT access + httpOnly rotating refresh; reuse of old refresh revokes sessions.",
            "IP rate limits (auth / public / api) with 429 + Retry-After.",
            "Uploads: size cap + magic bytes; keys under products/{id}/ only.",
            "Access token in memory on the client (not localStorage).",
        ],
    ),
    (
        "Load / stress",
        [
            "seed_load — bulk LOAD-* products for list/dashboard pressure.",
            "stress_test — concurrent GETs; writes docs/load-results.md.",
            "For pure throughput set RATE_LIMIT_ENABLED=false during the run.",
        ],
    ),
    (
        "Tests & CI",
        [
            "Backend: pytest (dpp_test). Frontend: Vitest + production build.",
            "GitHub Actions on main/master: backend + frontend jobs.",
        ],
    ),
]


def build() -> Path:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUT_PATH), pagesize=A4)
    _width, height = A4
    y = height - 18 * mm

    def ensure_space(need: float = 16 * mm) -> None:
        nonlocal y
        if y < need:
            c.showPage()
            y = height - 18 * mm

    def heading(text: str) -> None:
        nonlocal y
        ensure_space(24 * mm)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(18 * mm, y, text)
        y -= 7 * mm

    def bullet(text: str) -> None:
        nonlocal y
        ensure_space()
        c.setFont("Helvetica", 10)
        max_chars = 95
        words = text.split()
        line = ""
        lines: list[str] = []
        for word in words:
            trial = f"{line} {word}".strip()
            if len(trial) <= max_chars:
                line = trial
            else:
                if line:
                    lines.append(line)
                line = word
        if line:
            lines.append(line)
        for i, part in enumerate(lines):
            prefix = "• " if i == 0 else "  "
            c.drawString(20 * mm, y, prefix + part)
            y -= 5 * mm
        y -= 1 * mm

    for title, lines in SECTIONS:
        heading(title)
        for line in lines:
            bullet(line)
        y -= 3 * mm

    c.save()
    return OUT_PATH


if __name__ == "__main__":
    path = build()
    print(f"wrote {path}")
