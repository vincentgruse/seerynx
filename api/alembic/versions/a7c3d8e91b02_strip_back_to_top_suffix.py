"""strip trailing 'Back to top' from species_info text fields

Revision ID: a7c3d8e91b02
Revises: f3a1b9c7d2e4
Create Date: 2026-06-12

"""

from typing import Sequence, Union
from alembic import op

revision: str = "a7c3d8e91b02"
down_revision: Union[str, None] = "f3a1b9c7d2e4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

COLUMNS = ["habitat", "food", "nesting", "behavior", "conservation"]


def upgrade() -> None:
    for column in COLUMNS:
        op.execute(
            f"UPDATE species_info SET {column} = trim(regexp_replace({column}, '\\s*Back to top\\s*$', '')) "
            f"WHERE {column} ~ 'Back to top\\s*$'"
        )


def downgrade() -> None:
    pass
