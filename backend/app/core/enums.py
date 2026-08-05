"""Fixed lists stored as readable text in Postgres (not 1, 2, 3).

Example: status is 'draft' / 'published'. Easier to read in the DB and in APIs.
"""

import enum


class UserRole(str, enum.Enum):
    """Who can do what: admin vs editor."""

    ADMIN = "admin"
    EDITOR = "editor"


class ProductStatus(str, enum.Enum):
    """Draft = editing; published = passport/QR exists."""

    DRAFT = "draft"
    PUBLISHED = "published"


class ProductCategory(str, enum.Enum):
    """Product type for filters and forms."""

    ELECTRONICS = "electronics"
    TEXTILE = "textile"
    FURNITURE = "furniture"
    FOOD = "food"
    AUTOMOTIVE = "automotive"
    OTHER = "other"


class DocumentType(str, enum.Enum):
    """Kind of file attached to a product."""

    USER_MANUAL = "user_manual"
    WARRANTY = "warranty"
    TECHNICAL_DATASHEET = "technical_datasheet"


class ImageType(str, enum.Enum):
    """Cover = main image; gallery = extra photos."""

    COVER = "cover"
    GALLERY = "gallery"


class PassportStatus(str, enum.Enum):
    """Whether the public passport link is still valid."""

    ACTIVE = "active"
    REVOKED = "revoked"


class VerificationStatus(str, enum.Enum):
    """Shown on the public passport page (e.g. verified badge)."""

    VERIFIED = "verified"
    UNVERIFIED = "unverified"
