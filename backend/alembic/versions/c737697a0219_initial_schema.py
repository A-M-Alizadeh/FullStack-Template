"""initial schema

Revision ID: c737697a0219
Revises:
Create Date: 2026-08-05 16:19:47.822996

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "c737697a0219"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

user_role = postgresql.ENUM("admin", "editor", name="user_role", create_type=False)
product_category = postgresql.ENUM(
    "electronics",
    "textile",
    "furniture",
    "food",
    "automotive",
    "other",
    name="product_category",
    create_type=False,
)
product_status = postgresql.ENUM(
    "draft", "published", name="product_status", create_type=False
)
document_type = postgresql.ENUM(
    "user_manual",
    "warranty",
    "technical_datasheet",
    name="document_type",
    create_type=False,
)
image_type = postgresql.ENUM("cover", "gallery", name="image_type", create_type=False)
passport_status = postgresql.ENUM(
    "active", "revoked", name="passport_status", create_type=False
)
verification_status = postgresql.ENUM(
    "verified", "unverified", name="verification_status", create_type=False
)


def upgrade() -> None:
    bind = op.get_bind()
    user_role.create(bind, checkfirst=True)
    product_category.create(bind, checkfirst=True)
    product_status.create(bind, checkfirst=True)
    document_type.create(bind, checkfirst=True)
    image_type.create(bind, checkfirst=True)
    passport_status.create(bind, checkfirst=True)
    verification_status.create(bind, checkfirst=True)

    op.create_table(
        "certification_types",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "issuing_authorities",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", user_role, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "products",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("sku", sa.String(length=100), nullable=False),
        sa.Column("serial_number", sa.String(length=100), nullable=False),
        sa.Column("category", product_category, nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("production_date", sa.Date(), nullable=False),
        sa.Column("country_of_origin", sa.String(length=2), nullable=False),
        sa.Column("status", product_status, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_products_created_by_id"), "products", ["created_by_id"], unique=False
    )
    op.create_index(op.f("ix_products_sku"), "products", ["sku"], unique=True)

    op.create_table(
        "materials",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("percentage", sa.Numeric(5, 2), nullable=False),
        sa.Column("country_of_origin", sa.String(length=2), nullable=False),
        sa.Column("recyclable", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_materials_product_id"), "materials", ["product_id"], unique=False
    )

    op.create_table(
        "sustainability",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("carbon_footprint", sa.String(length=100), nullable=False),
        sa.Column("water_consumption", sa.String(length=100), nullable=False),
        sa.Column("recycled_material_percent", sa.Numeric(5, 2), nullable=False),
        sa.Column("repairability_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("recyclable", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("product_id"),
    )
    op.create_index(
        op.f("ix_sustainability_product_id"),
        "sustainability",
        ["product_id"],
        unique=False,
    )

    op.create_table(
        "certifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "certification_type_id", postgresql.UUID(as_uuid=True), nullable=False
        ),
        sa.Column(
            "issuing_authority_id", postgresql.UUID(as_uuid=True), nullable=False
        ),
        sa.Column("issue_date", sa.Date(), nullable=False),
        sa.Column("expiration_date", sa.Date(), nullable=True),
        sa.Column("pdf_path", sa.String(length=500), nullable=False),
        sa.ForeignKeyConstraint(
            ["certification_type_id"], ["certification_types.id"]
        ),
        sa.ForeignKeyConstraint(
            ["issuing_authority_id"], ["issuing_authorities.id"]
        ),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_certifications_certification_type_id"),
        "certifications",
        ["certification_type_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_certifications_issuing_authority_id"),
        "certifications",
        ["issuing_authority_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_certifications_product_id"),
        "certifications",
        ["product_id"],
        unique=False,
    )

    op.create_table(
        "documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("doc_type", document_type, nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_documents_product_id"), "documents", ["product_id"], unique=False
    )

    op.create_table(
        "product_images",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("image_type", image_type, nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_product_images_product_id"),
        "product_images",
        ["product_id"],
        unique=False,
    )

    op.create_table(
        "passports",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("public_uuid", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("qr_code_path", sa.String(length=500), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("status", passport_status, nullable=False),
        sa.Column("verification_status", verification_status, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("product_id"),
    )
    op.create_index(
        op.f("ix_passports_product_id"), "passports", ["product_id"], unique=False
    )
    op.create_index(
        op.f("ix_passports_public_uuid"), "passports", ["public_uuid"], unique=True
    )

    op.create_table(
        "qr_scans",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("passport_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "scanned_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("ip_address", sa.String(length=45), nullable=False),
        sa.Column("browser", sa.String(length=100), nullable=False),
        sa.Column("operating_system", sa.String(length=100), nullable=False),
        sa.Column("browser_language", sa.String(length=20), nullable=False),
        sa.Column("country", sa.String(length=2), nullable=False),
        sa.ForeignKeyConstraint(["passport_id"], ["passports.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_qr_scans_passport_id"), "qr_scans", ["passport_id"], unique=False
    )
    op.create_index(
        op.f("ix_qr_scans_scanned_at"), "qr_scans", ["scanned_at"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_qr_scans_scanned_at"), table_name="qr_scans")
    op.drop_index(op.f("ix_qr_scans_passport_id"), table_name="qr_scans")
    op.drop_table("qr_scans")

    op.drop_index(op.f("ix_passports_public_uuid"), table_name="passports")
    op.drop_index(op.f("ix_passports_product_id"), table_name="passports")
    op.drop_table("passports")

    op.drop_index(op.f("ix_product_images_product_id"), table_name="product_images")
    op.drop_table("product_images")

    op.drop_index(op.f("ix_documents_product_id"), table_name="documents")
    op.drop_table("documents")

    op.drop_index(op.f("ix_certifications_product_id"), table_name="certifications")
    op.drop_index(
        op.f("ix_certifications_issuing_authority_id"), table_name="certifications"
    )
    op.drop_index(
        op.f("ix_certifications_certification_type_id"), table_name="certifications"
    )
    op.drop_table("certifications")

    op.drop_index(op.f("ix_sustainability_product_id"), table_name="sustainability")
    op.drop_table("sustainability")

    op.drop_index(op.f("ix_materials_product_id"), table_name="materials")
    op.drop_table("materials")

    op.drop_index(op.f("ix_products_sku"), table_name="products")
    op.drop_index(op.f("ix_products_created_by_id"), table_name="products")
    op.drop_table("products")

    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")

    op.drop_table("issuing_authorities")
    op.drop_table("certification_types")

    bind = op.get_bind()
    verification_status.drop(bind, checkfirst=True)
    passport_status.drop(bind, checkfirst=True)
    image_type.drop(bind, checkfirst=True)
    document_type.drop(bind, checkfirst=True)
    product_status.drop(bind, checkfirst=True)
    product_category.drop(bind, checkfirst=True)
    user_role.drop(bind, checkfirst=True)
