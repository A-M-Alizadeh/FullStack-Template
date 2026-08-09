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

    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: int = 5432
    postgres_db: str

    cors_origins: list[str]
    frontend_url: str
    upload_dir: str = "uploads"

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

    # Cross-origin SPA (e.g. :3000 → :8000) needs SameSite=none + Secure.
    # Chromium treats http://localhost as OK for Secure cookies.
    cookie_secure: bool = True
    cookie_samesite: str = "none"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
