"""Simple concurrent HTTP stress harness against a running API.

Uses httpx (dev dependency). Prefer temporarily raising or disabling rate limits
for pure throughput tests:

  RATE_LIMIT_ENABLED=false

Examples (API must be up):
  APP_ENV=local uv run python -m scripts.stress_test
  APP_ENV=local uv run python -m scripts.stress_test --workers 20 --requests 200
  APP_ENV=local uv run python -m scripts.stress_test --base-url http://127.0.0.1:8000

Writes a markdown snippet to docs/load-results.md (repo root docs/).
"""

from __future__ import annotations

import argparse
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import httpx

PROJECT_DOCS = Path(__file__).resolve().parents[2] / "docs"
RESULTS_PATH = PROJECT_DOCS / "load-results.md"


@dataclass
class Sample:
    name: str
    status: int
    elapsed_ms: float


def _percentile(sorted_vals: list[float], pct: float) -> float:
    if not sorted_vals:
        return 0.0
    k = (len(sorted_vals) - 1) * (pct / 100.0)
    f = int(k)
    c = min(f + 1, len(sorted_vals) - 1)
    if f == c:
        return sorted_vals[f]
    return sorted_vals[f] + (sorted_vals[c] - sorted_vals[f]) * (k - f)


def _login(client: httpx.Client, email: str, password: str) -> str:
    try:
        r = client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
        )
    except httpx.ConnectError as exc:
        raise SystemExit(
            f"Cannot reach API at {client.base_url}.\n"
            "Start it first in another terminal, then re-run stress:\n"
            "  APP_ENV=local uv run uvicorn app.main:app --reload\n"
            f"Details: {exc}"
        ) from exc
    if r.status_code >= 400:
        raise SystemExit(
            f"Login failed ({r.status_code}): {r.text[:300]}\n"
            "Check seed users / email / password."
        )
    return r.json()["access_token"]


def _pick_public_uuid(client: httpx.Client, token: str) -> str | None:
    r = client.get(
        "/api/v1/products",
        headers={"Authorization": f"Bearer {token}"},
        params={"status": "published", "limit": 1},
    )
    r.raise_for_status()
    items = r.json().get("items") or []
    if not items:
        return None
    return items[0].get("public_uuid")


def _one(
    client: httpx.Client,
    name: str,
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
) -> Sample:
    t0 = time.perf_counter()
    r = client.request(method, url, headers=headers)
    ms = (time.perf_counter() - t0) * 1000
    return Sample(name=name, status=r.status_code, elapsed_ms=ms)


def run_stress(
    *,
    base_url: str,
    workers: int,
    requests_n: int,
    email: str,
    password: str,
) -> str:
    base = base_url.rstrip("/")
    summary_lines: list[str] = []

    with httpx.Client(base_url=base, timeout=30.0) as client:
        token = _login(client, email, password)
        auth = {"Authorization": f"Bearer {token}"}
        public_uuid = _pick_public_uuid(client, token)

        jobs: list[tuple[str, str, str, dict[str, str] | None]] = []
        # Mix of authenticated list + dashboard + optional public passport.
        for i in range(requests_n):
            kind = i % 3
            if kind == 0:
                jobs.append(("products_list", "GET", "/api/v1/products?limit=20", auth))
            elif kind == 1:
                jobs.append(("dashboard", "GET", "/api/v1/dashboard", auth))
            else:
                if public_uuid:
                    jobs.append(
                        (
                            "public_passport",
                            "GET",
                            f"/api/v1/passport/{public_uuid}",
                            None,
                        )
                    )
                else:
                    jobs.append(
                        ("products_list", "GET", "/api/v1/products?limit=20", auth)
                    )

        samples: list[Sample] = []
        t0 = time.perf_counter()
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = [
                pool.submit(_one, client, name, method, path, headers=headers)
                for name, method, path, headers in jobs
            ]
            for fut in as_completed(futures):
                samples.append(fut.result())
        wall = time.perf_counter() - t0

    by_name: dict[str, list[Sample]] = {}
    for s in samples:
        by_name.setdefault(s.name, []).append(s)

    rps = len(samples) / wall if wall else 0.0
    stamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    summary_lines.append(f"## Run — {stamp}")
    summary_lines.append("")
    summary_lines.append(f"- Base URL: `{base}`")
    summary_lines.append(f"- Workers: **{workers}**")
    summary_lines.append(f"- Requests: **{len(samples)}**")
    summary_lines.append(f"- Wall time: **{wall:.2f}s**")
    summary_lines.append(f"- Overall throughput: **{rps:.1f} req/s**")
    summary_lines.append("")
    summary_lines.append("| Endpoint | OK | Errors | p50 (ms) | p95 (ms) | max (ms) |")
    summary_lines.append("|----------|----|--------|----------|----------|----------|")

    for name, rows in sorted(by_name.items()):
        ok = sum(1 for r in rows if 200 <= r.status < 300)
        err = len(rows) - ok
        times = sorted(r.elapsed_ms for r in rows)
        summary_lines.append(
            f"| `{name}` | {ok} | {err} | {_percentile(times, 50):.1f} | "
            f"{_percentile(times, 95):.1f} | {max(times):.1f} |"
        )

    statuses = sorted({s.status for s in samples})
    summary_lines.append("")
    summary_lines.append(f"Status codes seen: {', '.join(str(s) for s in statuses)}")
    if 429 in statuses:
        summary_lines.append(
            "Note: `429` means rate limiting engaged — raise limits or set "
            "`RATE_LIMIT_ENABLED=false` for a pure throughput run."
        )
    summary_lines.append("")
    summary_lines.append(
        f"Mean latency (all): **{statistics.mean(s.elapsed_ms for s in samples):.1f} ms**"
    )
    summary_lines.append("")

    block = "\n".join(summary_lines) + "\n"
    PROJECT_DOCS.mkdir(parents=True, exist_ok=True)
    header = (
        "# Load results\n\n"
        "Generated by `python -m scripts.stress_test`. "
        "New runs are **prepended** (newest first).\n\n"
    )
    previous = ""
    if RESULTS_PATH.is_file():
        existing = RESULTS_PATH.read_text(encoding="utf-8")
        # Keep prior ## Run sections; drop old single-run body without headings.
        if "## Run —" in existing:
            idx = existing.find("## Run —")
            previous = existing[idx:]
        elif existing.strip() and "No stress run" not in existing:
            # Migrate first run format into a section.
            previous = "## Run — previous\n\n" + existing.split("\n", 2)[-1]

    RESULTS_PATH.write_text(header + block + previous, encoding="utf-8")
    print(block)
    print(f"wrote {RESULTS_PATH}")
    return block


def main() -> None:
    parser = argparse.ArgumentParser(description="Concurrent API stress harness.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument(
        "--workers",
        type=int,
        default=8,
        help="Concurrent workers (keep low on a laptop; default 8)",
    )
    parser.add_argument(
        "--requests",
        type=int,
        default=80,
        help="Total HTTP requests (default 80 — gentle on a Mac)",
    )
    parser.add_argument("--email", default="admin@example.com")
    parser.add_argument("--password", default="admin1234")
    args = parser.parse_args()
    if args.workers > 40 or args.requests > 2000:
        raise SystemExit(
            "Refusing oversized run on a laptop "
            f"(workers={args.workers}, requests={args.requests}). "
            "Use --workers <= 40 and --requests <= 2000."
        )
    run_stress(
        base_url=args.base_url,
        workers=args.workers,
        requests_n=args.requests,
        email=args.email,
        password=args.password,
    )


if __name__ == "__main__":
    main()
