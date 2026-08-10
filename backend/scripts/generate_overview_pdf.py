"""Generate docs/DPP_Project_Overview.pdf for assessment handoff.

  APP_ENV=local uv run python -m scripts.generate_overview_pdf
"""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

# scripts/ → backend/ → repo root
PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUT_PATH = PROJECT_ROOT / "docs" / "DPP_Project_Overview.pdf"

SECTIONS: list[tuple[str, list[str]]] = [
    (
        "Digital Product Passport — Project Overview",
        [
            "Full-stack platform to create, publish, and share product passports via QR.",
            "Stack: FastAPI + PostgreSQL + Alembic · Next.js + TypeScript + MUI + RTK Query.",
            "Local run: Postgres in Docker; API and web on the host (see root README).",
        ],
    ),
    (
        "How to run (reviewers)",
        [
            "1. Copy .env.example and backend/frontend .env.local.example files",
            "2. docker compose up db",
            "3. backend: uv sync && alembic upgrade head && seed_* && uvicorn",
            "4. frontend: npm i && npm run dev",
            "5. Open http://localhost:3000 and http://localhost:8000/docs",
            "Logins: admin@example.com / admin1234 · editor@example.com / editor1234",
        ],
    ),
    (
        "Core features",
        [
            "Auth: JWT access + httpOnly refresh cookie; roles admin | editor",
            "Products with materials, sustainability, certifications, docs, images",
            "Publish → stable public UUID + QR; public passport page; scan tracking",
            "Dashboard and analytics; admin user CRUD",
        ],
    ),
    (
        "Bonuses implemented",
        [
            "Soft delete + restore/Undo; search and pagination on product list",
            "Audit log table + admin /audit UI",
            "Drag-and-drop uploads; passport versioning (republish, same QR URL)",
            "Passport PDF export (BackgroundTasks cache)",
            "Redis cache for dashboard/analytics (optional REDIS_URL)",
            "MinIO-ready Storage backend (STORAGE_BACKEND=minio)",
            "Purge job: hard-delete soft-deleted products after retention days",
        ],
    ),
    (
        "Soft delete & purge",
        [
            "DELETE sets products.deleted_at (row kept; hidden from lists/passport).",
            "Restore clears deleted_at (UI Undo snackbar).",
            "CLI purge removes old soft-deleted rows + stored files:",
            "  APP_ENV=local uv run python -m scripts.purge_deleted_products --dry-run",
            "Retention: SOFT_DELETE_RETENTION_DAYS (default 30).",
        ],
    ),
    (
        "Demo walkthrough",
        [
            "1. Login as admin → Dashboard / Analytics",
            "2. Products → DEMO-001 → Publish panel (versions, QR, republish)",
            "3. Soft-delete a product → Undo; open Audit",
            "4. Public passport → Download PDF; visit with ?src=qr",
            "5. Login as editor → Users and Audit hidden",
        ],
    ),
    (
        "Docs & tests",
        [
            "Architecture: docs/ARCHITECTURE.md · Database: backend/docs/database.md",
            "Overview PDF: docs/DPP_Project_Overview.pdf (this file)",
            "Backend tests: cd backend && APP_ENV=local uv run pytest",
            "Frontend: npm test · Playwright: npm run test:e2e (API+seeds up)",
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
