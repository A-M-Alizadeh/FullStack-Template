FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.8.4 /uv /uvx /bin/

FROM base AS deps
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

FROM base AS runtime
COPY --from=deps /app/.venv /app/.venv
COPY app ./app
COPY alembic ./alembic
COPY pyproject.toml uv.lock ./

ENV PATH="/app/.venv/bin:$PATH" \
    PORT=8000 \
    WEB_CONCURRENCY=2

EXPOSE 8000

# Production: Gunicorn + Uvicorn workers (override WEB_CONCURRENCY as needed).
CMD ["sh", "-c", "gunicorn -k uvicorn.workers.UvicornWorker -w ${WEB_CONCURRENCY} -b 0.0.0.0:${PORT} --timeout 60 app.main:app"]
