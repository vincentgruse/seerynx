"""initial schema

Revision ID: 94654bf27f5f
Revises:
Create Date: 2026-06-10

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "94654bf27f5f"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sightings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "timestamp", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("common_name", sa.String(), nullable=False),
        sa.Column("scientific_name", sa.String(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("photo_path", sa.String(), nullable=True),
        sa.Column("lat", sa.Float(), nullable=True),
        sa.Column("lon", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("source IN ('vision', 'audio')", name="source_check"),
    )
    op.create_index("idx_sightings_timestamp", "sightings", ["timestamp"])
    op.create_index("idx_sightings_species", "sightings", ["common_name"])

    op.create_table(
        "species_info",
        sa.Column("common_name", sa.String(), nullable=False),
        sa.Column("scientific_name", sa.String(), nullable=True),
        sa.Column("ebird_code", sa.String(), nullable=True),
        sa.Column("habitat", sa.Text(), nullable=True),
        sa.Column("food", sa.Text(), nullable=True),
        sa.Column("nesting", sa.Text(), nullable=True),
        sa.Column("behavior", sa.Text(), nullable=True),
        sa.Column("conservation", sa.Text(), nullable=True),
        sa.Column("foods_list", sa.Text(), nullable=True),
        sa.Column("feeder_types", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("common_name"),
    )

    op.create_table(
        "weather",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "timestamp", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("temperature_c", sa.Float(), nullable=False),
        sa.Column("humidity", sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_weather_timestamp", "weather", ["timestamp"])


def downgrade() -> None:
    op.drop_index("idx_weather_timestamp", table_name="weather")
    op.drop_table("weather")
    op.drop_table("species_info")
    op.drop_index("idx_sightings_species", table_name="sightings")
    op.drop_index("idx_sightings_timestamp", table_name="sightings")
    op.drop_table("sightings")
