"""add species category

Revision ID: f3a1b9c7d2e4
Revises: e2f00289997f
Create Date: 2026-06-12

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "f3a1b9c7d2e4"
down_revision: Union[str, None] = "e2f00289997f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "species_info", sa.Column("category", sa.String(length=50), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("species_info", "category")
