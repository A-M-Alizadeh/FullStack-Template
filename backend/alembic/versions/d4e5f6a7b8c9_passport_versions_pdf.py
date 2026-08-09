"""passport versions + pdf_path

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-08-09

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, Sequence[str], None] = "c3d4e5f6a7b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "passports",
        sa.Column("pdf_path", sa.String(length=500), nullable=True),
    )
    op.drop_constraint("passports_product_id_key", "passports", type_="unique")
    op.drop_index(op.f("ix_passports_public_uuid"), table_name="passports")
    op.create_index(
        op.f("ix_passports_public_uuid"), "passports", ["public_uuid"], unique=False
    )
    op.create_unique_constraint(
        "uq_passports_product_version", "passports", ["product_id", "version"]
    )
    op.create_unique_constraint(
        "uq_passports_public_uuid_version", "passports", ["public_uuid", "version"]
    )
    op.create_index(
        "uq_passports_product_active",
        "passports",
        ["product_id"],
        unique=True,
        postgresql_where=sa.text("status = 'active'"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_passports_product_active",
        table_name="passports",
        postgresql_where=sa.text("status = 'active'"),
    )
    op.drop_constraint("uq_passports_public_uuid_version", "passports", type_="unique")
    op.drop_constraint("uq_passports_product_version", "passports", type_="unique")
    op.drop_index(op.f("ix_passports_public_uuid"), table_name="passports")
    op.create_index(
        op.f("ix_passports_public_uuid"), "passports", ["public_uuid"], unique=True
    )
    op.create_unique_constraint("passports_product_id_key", "passports", ["product_id"])
    op.drop_column("passports", "pdf_path")
