from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field


class Coordinates(BaseModel):
    lat: float
    lon: float
    accuracy: float | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RegisterRequest(BaseModel):
    name: str
    phone: str
    password: str
    region: str | None = None
    emergency_contacts: list[dict[str, Any]] = Field(default_factory=list)
    checkin_interval: int = 3600


class LoginRequest(BaseModel):
    phone: str
    password: str


class UserRead(BaseModel):
    id: UUID
    name: str
    phone: str
    region: str | None = None
    emergency_contacts: list[dict[str, Any]] = Field(default_factory=list)
    checkin_interval: int
    last_seen: datetime | None = None
    device_token: str | None = None
    is_admin: bool = False
    is_active: bool = True
    created_at: datetime | None = None


class AlertCreate(BaseModel):
    gps_coords: Coordinates | None = None
    battery_level: int | None = None
    alert_type: Literal["SOS"] = "SOS"
    message: str | None = None


class CheckinRequest(BaseModel):
    timestamp: datetime | None = None


class MeshAlertRequest(BaseModel):
    uid: str
    lat: float | None = None
    lon: float | None = None
    type: Literal["SOS", "OK", "ZONE_ALERT"]
    ts: datetime | None = None
    battery_level: int | None = None
    message: str | None = None


class SmsInboundRequest(BaseModel):
    from_phone: str
    text: str
    region: str | None = None


class RoutePoint(BaseModel):
    lat: float
    lon: float


class RouteUpsertRequest(BaseModel):
    name: str
    destination: str | None = None
    expected_arrival: datetime | None = None
    points: list[RoutePoint]
    active: bool = True


class DangerZoneRequest(BaseModel):
    name: str
    description: str | None = None
    severity: Literal["low", "medium", "high"] = "medium"
    active: bool = True
    coordinates: list[list[list[float]]]


class ResponderRequest(BaseModel):
    name: str
    phone: str
    region: str | None = None
    device_token: str | None = None


class AlertRead(BaseModel):
    id: UUID
    user_id: UUID | None = None
    type: str
    source: str
    status: str
    message: str | None = None
    location: dict[str, Any] | None = None
    accuracy: float | None = None
    battery: int | None = None
    created_at: datetime


class DangerZoneRead(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    severity: str
    active: bool
    geometry: dict[str, Any]


class RouteRead(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    destination: str | None = None
    expected_arrival: datetime | None = None
    active: bool
    points: list[RoutePoint]


class ResponderRead(BaseModel):
    id: UUID
    name: str
    phone: str
    region: str | None = None
    device_token: str | None = None
    active: bool
