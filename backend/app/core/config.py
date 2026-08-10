import os
from functools import lru_cache
from pathlib import Path

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


def _env_files() -> tuple[str, ...]:
    app_env = os.getenv("APP_ENV", "local")
    return (
        str(BASE_DIR / f".env.{app_env}"),
        str(BASE_DIR / ".env"),
    )


def normalize_database_url(raw: str) -> str:
    """Turn a managed-Postgres URL into a SQLAlchemy + psycopg URL."""
    url = raw.strip()
    if not url:
        return url
    if url.startswith("postgresql+psycopg://"):
        return url
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url.removeprefix("postgres://")
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url.removeprefix("postgresql://")
    return url


class Settings(BaseSettings):
    """All runtime values come from environment / .env.{APP_ENV} files."""

    model_config = SettingsConfigDict(
        env_file=_env_files(),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: str
    app_name: str
    app_version: str
    debug: bool = False
    api_prefix: str = "/api/v1"

    # Used when DATABASE_URL is unset (local docker-compose).
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "dpp"

    # Managed hosts (Render/Railway) inject this; takes precedence when set.
    database_url_override: str = Field(default="", validation_alias="DATABASE_URL")

    cors_origins: list[str]
    frontend_url: str
    upload_dir: str = "uploads"
    max_upload_bytes: int = Field(default=10 * 1024 * 1024, ge=1024)  # 10 MiB

    # Soft-deleted products older than this many days are eligible for hard purge.
    soft_delete_retention_days: int = Field(default=30, ge=1)

    # Rate limits (SlowAPI strings). Disabled when rate_limit_enabled is false.
    rate_limit_enabled: bool = True
    rate_limit_auth: str = "10/minute"
    rate_limit_public: str = "60/minute"
    rate_limit_api: str = "120/minute"

    # Cache / object storage (optional bonuses; empty = disabled / local disk).
    redis_url: str = ""
    storage_backend: str = "local"  # local | minio
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "dpp"
    minio_secure: bool = False

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = Field(default=60, ge=1)
    refresh_expire_days: int = Field(default=14, ge=1)

    # Cross-origin SPA (e.g. Vercel → Render) needs SameSite=none + Secure.
    # Chromium treats http://localhost as OK for Secure cookies.
    cookie_secure: bool = True
    cookie_samesite: str = "none"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def database_url(self) -> str:
        if self.database_url_override.strip():
            return normalize_database_url(self.database_url_override)
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
