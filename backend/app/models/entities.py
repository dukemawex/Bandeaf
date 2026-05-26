from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import uuid4

from geoalchemy2 import Geometry
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class AlertType(str, Enum):
    SOS = "SOS"
    MISSED_CHECKIN = "MISSED_CHECKIN"
    ZONE_ENTRY = "ZONE_ENTRY"


class AlertSource(str, Enum):
    app = "app"
    mesh = "mesh"
    sms = "sms"


class AlertStatus(str, Enum):
    active = "active"
    acknowledged = "acknowledged"
    resolved = "resolved"


class ZoneSeverity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class NotificationChannel(str, Enum):
    sms = "sms"
    fcm = "fcm"
    email = "email"


class NotificationStatus(str, Enum):
    sent = "sent"
    failed = "failed"
    pending = "pending"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=False, unique=True, index=True)
    region: Mapped[str | None] = mapped_column(String(100), nullable=True)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    emergency_contacts: Mapped[list[dict] | None] = mapped_column(JSONB, default=list)
    checkin_interval: Mapped[int] = mapped_column(Integer, default=3600)
    last_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    device_token: Mapped[str | None] = mapped_column(String(512), nullable=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    type: Mapped[AlertType] = mapped_column(String(32), nullable=False)
    location: Mapped[str | None] = mapped_column(Geometry(geometry_type="POINT", srid=4326), nullable=True)
    accuracy: Mapped[float | None] = mapped_column(nullable=True)
    battery: Mapped[int | None] = mapped_column(nullable=True)
    source: Mapped[AlertSource] = mapped_column(String(16), default=AlertSource.app.value)
    status: Mapped[AlertStatus] = mapped_column(String(32), default=AlertStatus.active.value)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class DangerZone(Base):
    __tablename__ = "danger_zones"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    boundary: Mapped[str] = mapped_column(Geometry(geometry_type="POLYGON", srid=4326), nullable=False)
    severity: Mapped[ZoneSeverity] = mapped_column(String(16), default=ZoneSeverity.medium.value)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PlannedRoute(Base):
    __tablename__ = "planned_routes"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    path: Mapped[str] = mapped_column(Geometry(geometry_type="LINESTRING", srid=4326), nullable=False)
    destination: Mapped[str | None] = mapped_column(String(255), nullable=True)
    expected_arrival: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    alert_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("alerts.id", ondelete="CASCADE"), nullable=False)
    recipient_phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    recipient_device_token: Mapped[str | None] = mapped_column(String(512), nullable=True)
    channel: Mapped[NotificationChannel] = mapped_column(String(16), nullable=False)
    status: Mapped[NotificationStatus] = mapped_column(String(16), default=NotificationStatus.pending.value)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Responder(Base):
    __tablename__ = "responders"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    region: Mapped[str | None] = mapped_column(String(100), nullable=True)
    device_token: Mapped[str | None] = mapped_column(String(512), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
