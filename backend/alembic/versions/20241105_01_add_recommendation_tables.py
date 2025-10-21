"""
Add flight and accommodation recommendation tables
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20241105_01"
down_revision: Union[str, None] = "20241031_02"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create tables for flight and accommodation recommendations"""
    op.create_table(
        "flight_options",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("travel_plan_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "provider",
            sa.String(length=50),
            nullable=False,
            server_default=sa.text("'Skyscanner'"),
        ),
        sa.Column("carrier", sa.String(length=100), nullable=False),
        sa.Column("flight_number", sa.String(length=20), nullable=False),
        sa.Column("departure_airport", sa.String(length=10), nullable=False),
        sa.Column("arrival_airport", sa.String(length=10), nullable=False),
        sa.Column("departure_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("arrival_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column(
            "stops",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column("seat_class", sa.String(length=50), nullable=True),
        sa.Column("baggage_info", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "price_currency",
            sa.String(length=3),
            nullable=False,
            server_default=sa.text("'KRW'"),
        ),
        sa.Column("price_amount", sa.Integer(), nullable=False),
        sa.Column("booking_url", sa.Text(), nullable=False),
        sa.Column("affiliate_code", sa.String(length=50), nullable=True),
        sa.Column(
            "last_synced_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["travel_plan_id"],
            ["travel_plans.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("price_amount >= 0", name="ck_flight_option_price_non_negative"),
        sa.CheckConstraint("duration_minutes > 0", name="ck_flight_option_duration_positive"),
        sa.CheckConstraint("stops >= 0", name="ck_flight_option_stops_non_negative"),
    )
    op.create_index(
        "ix_flight_options_plan_id",
        "flight_options",
        ["travel_plan_id"],
    )
    op.create_index(
        "ix_flight_options_price",
        "flight_options",
        ["price_amount"],
    )

    op.create_table(
        "accommodation_options",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("travel_plan_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "provider",
            sa.String(length=50),
            nullable=False,
            server_default=sa.text("'Booking.com'"),
        ),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("city", sa.String(length=100), nullable=True),
        sa.Column("country", sa.String(length=100), nullable=True),
        sa.Column("latitude", sa.Numeric(10, 8), nullable=True),
        sa.Column("longitude", sa.Numeric(11, 8), nullable=True),
        sa.Column("rating", sa.Numeric(2, 1), nullable=True),
        sa.Column("review_count", sa.Integer(), nullable=True),
        sa.Column("star_rating", sa.Numeric(2, 1), nullable=True),
        sa.Column(
            "price_currency",
            sa.String(length=3),
            nullable=False,
            server_default=sa.text("'KRW'"),
        ),
        sa.Column("price_per_night", sa.Integer(), nullable=True),
        sa.Column("total_price", sa.Integer(), nullable=False),
        sa.Column("check_in_date", sa.Date(), nullable=True),
        sa.Column("check_out_date", sa.Date(), nullable=True),
        sa.Column("nights", sa.Integer(), nullable=True),
        sa.Column("room_type", sa.String(length=100), nullable=True),
        sa.Column("booking_url", sa.Text(), nullable=False),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("amenities", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("tags", postgresql.ARRAY(sa.String(length=50)), nullable=True),
        sa.Column("policies", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "last_synced_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["travel_plan_id"],
            ["travel_plans.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "price_per_night IS NULL OR price_per_night >= 0",
            name="ck_accommodation_option_price_per_night",
        ),
        sa.CheckConstraint(
            "total_price >= 0",
            name="ck_accommodation_option_total_price",
        ),
        sa.CheckConstraint(
            "rating IS NULL OR (rating >= 0 AND rating <= 5)",
            name="ck_accommodation_option_rating",
        ),
        sa.CheckConstraint(
            "review_count IS NULL OR review_count >= 0",
            name="ck_accommodation_option_reviews",
        ),
        sa.CheckConstraint(
            "nights IS NULL OR nights >= 1",
            name="ck_accommodation_option_nights",
        ),
    )
    op.create_index(
        "ix_accommodation_options_plan_id",
        "accommodation_options",
        ["travel_plan_id"],
    )
    op.create_index(
        "ix_accommodation_options_total_price",
        "accommodation_options",
        ["total_price"],
    )


def downgrade() -> None:
    """Drop recommendation tables"""
    op.drop_index(
        "ix_accommodation_options_total_price",
        table_name="accommodation_options",
    )
    op.drop_index(
        "ix_accommodation_options_plan_id",
        table_name="accommodation_options",
    )
    op.drop_table("accommodation_options")

    op.drop_index("ix_flight_options_price", table_name="flight_options")
    op.drop_index("ix_flight_options_plan_id", table_name="flight_options")
    op.drop_table("flight_options")
