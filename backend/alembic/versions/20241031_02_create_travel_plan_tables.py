"""
Create travel plan core tables
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20241031_02"
down_revision: Union[str, None] = "20241031_01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create travel planning tables"""
    op.create_table(
        "travel_plans",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("destination", sa.String(length=100), nullable=False),
        sa.Column("country", sa.String(length=100), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("total_days", sa.Integer(), nullable=False),
        sa.Column("total_nights", sa.Integer(), nullable=False),
        sa.Column("budget_total", sa.Integer(), nullable=False),
        sa.Column("budget_allocated", sa.Integer(), nullable=True),
        sa.Column("budget_breakdown", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("traveler_type", sa.String(length=50), nullable=False),
        sa.Column("traveler_count", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("preferences", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default=sa.text("'draft'")),
        sa.Column("ai_model_version", sa.String(length=50), nullable=True),
        sa.Column("generation_time_seconds", sa.Numeric(5, 2), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("end_date >= start_date", name="ck_travel_plan_date_range"),
        sa.CheckConstraint("total_days > 0", name="ck_travel_plan_total_days"),
        sa.CheckConstraint("total_nights >= 0", name="ck_travel_plan_total_nights"),
        sa.CheckConstraint("budget_total > 0", name="ck_travel_plan_budget_total"),
        sa.CheckConstraint("traveler_count >= 1", name="ck_travel_plan_traveler_count"),
    )

    op.create_index("ix_travel_plans_user_id", "travel_plans", ["user_id"])
    op.create_index("ix_travel_plans_destination", "travel_plans", ["destination"])
    op.create_index("ix_travel_plans_created_at", "travel_plans", ["created_at"])

    op.create_table(
        "places",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("external_id", sa.String(length=100), nullable=True),
        sa.Column("external_source", sa.String(length=50), nullable=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("subcategory", sa.String(length=100), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("city", sa.String(length=100), nullable=True),
        sa.Column("country", sa.String(length=100), nullable=True),
        sa.Column("latitude", sa.Numeric(10, 8), nullable=False),
        sa.Column("longitude", sa.Numeric(11, 8), nullable=False),
        sa.Column("rating", sa.Numeric(2, 1), nullable=True),
        sa.Column("price_level", sa.Integer(), nullable=True),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("website", sa.Text(), nullable=True),
        sa.Column("opening_hours", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("photos", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("tags", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "latitude >= -90 AND latitude <= 90",
            name="ck_place_latitude",
        ),
        sa.CheckConstraint(
            "longitude >= -180 AND longitude <= 180",
            name="ck_place_longitude",
        ),
        sa.CheckConstraint(
            "rating IS NULL OR (rating >= 0 AND rating <= 5)",
            name="ck_place_rating",
        ),
        sa.CheckConstraint(
            "price_level IS NULL OR (price_level >= 1 AND price_level <= 4)",
            name="ck_place_price_level",
        ),
    )

    op.create_index("ix_places_external_id", "places", ["external_id"])
    op.create_index("ix_places_city", "places", ["city"])
    op.create_index("ix_places_category", "places", ["category"])

    op.create_table(
        "daily_itineraries",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("travel_plan_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("day_number", sa.Integer(), nullable=False),
        sa.Column("theme", sa.String(length=100), nullable=True),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("weather_forecast", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["travel_plan_id"], ["travel_plans.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("day_number >= 1", name="ck_daily_itinerary_day_number"),
    )

    op.create_index(
        "ix_daily_itineraries_travel_plan_id", "daily_itineraries", ["travel_plan_id"]
    )
    op.create_index(
        "ux_daily_itineraries_plan_day",
        "daily_itineraries",
        ["travel_plan_id", "day_number"],
        unique=True,
    )
    op.create_index(
        "ux_daily_itineraries_plan_date",
        "daily_itineraries",
        ["travel_plan_id", "date"],
        unique=True,
    )

    op.create_table(
        "itinerary_places",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("daily_itinerary_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("place_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("visit_order", sa.Integer(), nullable=False),
        sa.Column("visit_time", sa.Time(), nullable=True),
        sa.Column("duration_minutes", sa.Integer(), nullable=True),
        sa.Column("visit_type", sa.String(length=50), nullable=False),
        sa.Column("estimated_cost", sa.Integer(), nullable=True),
        sa.Column("ai_recommendation_reason", sa.Text(), nullable=True),
        sa.Column("user_notes", sa.Text(), nullable=True),
        sa.Column("is_confirmed", sa.Boolean(), nullable=False, server_default=sa.text("TRUE")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["daily_itinerary_id"], ["daily_itineraries.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["place_id"], ["places.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("visit_order >= 1", name="ck_itinerary_place_visit_order"),
        sa.CheckConstraint(
            "duration_minutes IS NULL OR duration_minutes > 0",
            name="ck_itinerary_place_duration",
        ),
    )

    op.create_index(
        "ix_itinerary_places_daily_itinerary_id",
        "itinerary_places",
        ["daily_itinerary_id"],
    )
    op.create_index("ix_itinerary_places_place_id", "itinerary_places", ["place_id"])
    op.create_index(
        "ux_itinerary_places_plan_order",
        "itinerary_places",
        ["daily_itinerary_id", "visit_order"],
        unique=True,
    )

    op.create_table(
        "routes",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("daily_itinerary_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("from_place_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("to_place_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("from_order", sa.Integer(), nullable=False),
        sa.Column("to_order", sa.Integer(), nullable=False),
        sa.Column("transport_mode", sa.String(length=50), nullable=False),
        sa.Column("distance_meters", sa.Integer(), nullable=True),
        sa.Column("duration_minutes", sa.Integer(), nullable=True),
        sa.Column("estimated_cost", sa.Integer(), nullable=True),
        sa.Column("route_polyline", sa.Text(), nullable=True),
        sa.Column("instructions", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["daily_itinerary_id"], ["daily_itineraries.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["from_place_id"], ["places.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["to_place_id"], ["places.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("from_place_id <> to_place_id", name="ck_route_distinct_places"),
        sa.CheckConstraint("from_order < to_order", name="ck_route_order_sequence"),
        sa.CheckConstraint(
            "duration_minutes IS NULL OR duration_minutes > 0",
            name="ck_route_duration_positive",
        ),
    )

    op.create_index("ix_routes_daily_itinerary_id", "routes", ["daily_itinerary_id"])
    op.create_index("ix_routes_from_place_id", "routes", ["from_place_id"])
    op.create_index("ix_routes_to_place_id", "routes", ["to_place_id"])


def downgrade() -> None:
    """Drop travel planning tables"""
    op.drop_index("ix_routes_to_place_id", table_name="routes")
    op.drop_index("ix_routes_from_place_id", table_name="routes")
    op.drop_index("ix_routes_daily_itinerary_id", table_name="routes")
    op.drop_table("routes")

    op.drop_index("ux_itinerary_places_plan_order", table_name="itinerary_places")
    op.drop_index("ix_itinerary_places_place_id", table_name="itinerary_places")
    op.drop_index("ix_itinerary_places_daily_itinerary_id", table_name="itinerary_places")
    op.drop_table("itinerary_places")

    op.drop_index(
        "ux_daily_itineraries_plan_date", table_name="daily_itineraries"
    )
    op.drop_index(
        "ux_daily_itineraries_plan_day", table_name="daily_itineraries"
    )
    op.drop_index(
        "ix_daily_itineraries_travel_plan_id", table_name="daily_itineraries"
    )
    op.drop_table("daily_itineraries")

    op.drop_index("ix_places_category", table_name="places")
    op.drop_index("ix_places_city", table_name="places")
    op.drop_index("ix_places_external_id", table_name="places")
    op.drop_table("places")

    op.drop_index("ix_travel_plans_created_at", table_name="travel_plans")
    op.drop_index("ix_travel_plans_destination", table_name="travel_plans")
    op.drop_index("ix_travel_plans_user_id", table_name="travel_plans")
    op.drop_table("travel_plans")
