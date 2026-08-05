"""Talk to Postgres: open a connection, give each request a DB session.

Settings (host, password, …) come from `app.core.config` / `.env.local`.
No extra db-settings file.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

# One engine for the whole app (connection pool).
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # drop dead connections
)

# Factory: each call makes a new Session (one unit of work).
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency: yield a session, always close it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
