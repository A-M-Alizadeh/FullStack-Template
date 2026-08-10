"""Unit tests for settings helpers."""

from app.core.config import normalize_database_url


def test_normalize_database_url_postgres_scheme():
    assert (
        normalize_database_url("postgres://u:p@h:5432/db")
        == "postgresql+psycopg://u:p@h:5432/db"
    )


def test_normalize_database_url_postgresql_scheme():
    assert (
        normalize_database_url("postgresql://u:p@h:5432/db")
        == "postgresql+psycopg://u:p@h:5432/db"
    )


def test_normalize_database_url_already_psycopg():
    url = "postgresql+psycopg://u:p@h:5432/db"
    assert normalize_database_url(url) == url


def test_normalize_database_url_strips_whitespace():
    assert (
        normalize_database_url("  postgres://u:p@h/db  ")
        == "postgresql+psycopg://u:p@h/db"
    )
