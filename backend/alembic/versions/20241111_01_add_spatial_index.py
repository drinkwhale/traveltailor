"""Add spatial index for places table"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "20241111_01"
down_revision = "20241105_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_places_location_gist
        ON places
        USING GIST (
            ST_SetSRID(
                ST_MakePoint(longitude::double precision, latitude::double precision),
                4326
            )
        );
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_places_location_gist")
