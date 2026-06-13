"""add species photo_path

Revision ID: e2f00289997f
Revises: 94654bf27f5f
Create Date: 2026-06-12

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "e2f00289997f"
down_revision: Union[str, None] = "94654bf27f5f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("species_info", sa.Column("photo_path", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("species_info", "photo_path")
