"""product soft delete + active SKU unique index

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-08-09

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "products",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        op.f("ix_products_deleted_at"), "products", ["deleted_at"], unique=False
    )
    # Replace global unique SKU index with partial unique (active rows only).
    op.drop_index(op.f("ix_products_sku"), table_name="products")
    op.create_index(
        "uq_products_sku_active",
        "products",
        ["sku"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.create_index(op.f("ix_products_sku"), "products", ["sku"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_products_sku"), table_name="products")
    op.drop_index("uq_products_sku_active", table_name="products")
    op.create_index(op.f("ix_products_sku"), "products", ["sku"], unique=True)
    op.drop_index(op.f("ix_products_deleted_at"), table_name="products")
    op.drop_column("products", "deleted_at")
