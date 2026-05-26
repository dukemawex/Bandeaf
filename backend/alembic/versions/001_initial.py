"""Initial schema with PostGIS

Revision ID: 001_initial
Revises:
Create Date: 2024-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import geoalchemy2

revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    op.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(30), nullable=False, unique=True),
        sa.Column("region", sa.String(100)),
        sa.Column("hashed_password", sa.String(255)),
        sa.Column("emergency_contacts", postgresql.JSONB, server_default="[]"),
        sa.Column("checkin_interval", sa.Integer, server_default="3600"),
        sa.Column("last_seen", sa.DateTime(timezone=True)),
        sa.Column("device_token", sa.String(512)),
        sa.Column("is_admin", sa.Boolean, server_default="false"),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_users_phone", "users", ["phone"], unique=True)

    alert_type = sa.Enum("SOS", "MISSED_CHECKIN", "ZONE_ENTRY", name="alert_type")
    alert_source = sa.Enum("app", "mesh", "sms", name="alert_source")
    alert_status = sa.Enum("active", "acknowledged", "resolved", name="alert_status")

    op.create_table(
        "alerts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("type", alert_type, nullable=False),
        sa.Column(
            "location",
            geoalchemy2.types.Geometry(geometry_type="POINT", srid=4326),
            nullable=True,
        ),
        sa.Column("accuracy", sa.Float),
        sa.Column("battery", sa.Integer),
        sa.Column("source", alert_source, server_default="app"),
        sa.Column("status", alert_status, server_default="active"),
        sa.Column("message", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_alerts_user_id", "alerts", ["user_id"])
    op.create_index("ix_alerts_status", "alerts", ["status"])

    zone_severity = sa.Enum("low", "medium", "high", "critical", name="zone_severity")

    op.create_table(
        "danger_zones",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column(
            "boundary",
            geoalchemy2.types.Geometry(geometry_type="POLYGON", srid=4326),
            nullable=False,
        ),
        sa.Column("severity", zone_severity, server_default="medium"),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("created_by", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "planned_routes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column(
            "path",
            geoalchemy2.types.Geometry(geometry_type="LINESTRING", srid=4326),
            nullable=False,
        ),
        sa.Column("destination", sa.String(255)),
        sa.Column("expected_arrival", sa.DateTime(timezone=True)),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    notif_channel = sa.Enum("sms", "fcm", "email", name="notif_channel")
    notif_status = sa.Enum("sent", "failed", "pending", name="notif_status")

    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("alert_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("alerts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("recipient_phone", sa.String(30)),
        sa.Column("recipient_device_token", sa.String(512)),
        sa.Column("channel", notif_channel, nullable=False),
        sa.Column("status", notif_status, server_default="pending"),
        sa.Column("error_message", sa.Text),
        sa.Column("sent_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_notifications_alert_id", "notifications", ["alert_id"])

    op.create_table(
        "responders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(30), nullable=False, unique=True),
        sa.Column("region", sa.String(100)),
        sa.Column("device_token", sa.String(512)),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )


def downgrade() -> None:
    op.drop_table("notifications")
    op.drop_table("responders")
    op.drop_table("planned_routes")
    op.drop_table("danger_zones")
    op.drop_table("alerts")
    op.drop_table("users")

    sa.Enum(name="notif_status").drop(op.get_bind())
    sa.Enum(name="notif_channel").drop(op.get_bind())
    sa.Enum(name="zone_severity").drop(op.get_bind())
    sa.Enum(name="alert_status").drop(op.get_bind())
    sa.Enum(name="alert_source").drop(op.get_bind())
    sa.Enum(name="alert_type").drop(op.get_bind())
