"""Parent class every SQLAlchemy model inherits from.

`Base.metadata` is what Alembic reads to know which tables exist.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared base for all tables."""

    pass
