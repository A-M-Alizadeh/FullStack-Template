"""Import models here so Alembic sees every table on `Base.metadata`.

Also re-exports engine / session helpers for the rest of the app.
"""

from app.database.base import Base
from app.database.session import SessionLocal, engine, get_db
from app.products.models import (
    Certification,
    CertificationType,
    Document,
    IssuingAuthority,
    Material,
    Passport,
    Product,
    ProductImage,
    QrScan,
    Sustainability,
)
from app.users.models import User

__all__ = [
    "Base",
    "SessionLocal",
    "engine",
    "get_db",
    "User",
    "Product",
    "Material",
    "Sustainability",
    "IssuingAuthority",
    "CertificationType",
    "Certification",
    "Document",
    "ProductImage",
    "Passport",
    "QrScan",
]
