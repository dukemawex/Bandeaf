from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from app.core.security import hash_password, verify_password


def _now() -> datetime:
    return datetime.now(tz=timezone.utc)


class InMemoryStore:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.users: dict[str, dict[str, Any]] = {}
        self.users_by_phone: dict[str, str] = {}
        self.alerts: dict[str, dict[str, Any]] = {}
        self.zones: dict[str, dict[str, Any]] = {}
        self.routes: dict[str, dict[str, Any]] = {}
        self.notifications: dict[str, dict[str, Any]] = {}
        self.responders: dict[str, dict[str, Any]] = {}
        self.event_log: list[dict[str, Any]] = []

    def create_user(
        self,
        *,
        name: str,
        phone: str,
        password: str,
        region: str | None = None,
        emergency_contacts: list[dict[str, Any]] | None = None,
        checkin_interval: int = 3600,
        is_admin: bool = False,
    ) -> dict[str, Any]:
        if phone in self.users_by_phone:
            raise ValueError("phone already registered")
        user_id = str(uuid4())
        user = {
            "id": user_id,
            "name": name,
            "phone": phone,
            "region": region,
            "hashed_password": hash_password(password),
            "emergency_contacts": emergency_contacts or [],
            "checkin_interval": checkin_interval,
            "last_seen": _now(),
            "device_token": None,
            "is_admin": is_admin,
            "is_active": True,
            "created_at": _now(),
        }
        self.users[user_id] = user
        self.users_by_phone[phone] = user_id
        return deepcopy(user)

    def authenticate(self, phone: str, password: str) -> dict[str, Any] | None:
        user_id = self.users_by_phone.get(phone)
        if not user_id:
            return None
        user = self.users[user_id]
        if not verify_password(password, user["hashed_password"]):
            return None
        return deepcopy(user)

    def get_user(self, user_id: str | None) -> dict[str, Any] | None:
        if not user_id:
            return None
        user = self.users.get(str(user_id))
        return deepcopy(user) if user else None

    def get_user_by_phone(self, phone: str) -> dict[str, Any] | None:
        user_id = self.users_by_phone.get(phone)
        return self.get_user(user_id)

    def list_users(self) -> list[dict[str, Any]]:
        return [deepcopy(user) for user in self.users.values()]

    def update_last_seen(self, user_id: str, timestamp: datetime | None = None) -> dict[str, Any]:
        user = self.users[user_id]
        user["last_seen"] = timestamp or _now()
        return deepcopy(user)

    def create_alert(
        self,
        *,
        user_id: str | None,
        alert_type: str,
        source: str,
        location: dict[str, Any] | None = None,
        accuracy: float | None = None,
        battery: int | None = None,
        message: str | None = None,
    ) -> dict[str, Any]:
        alert = {
            "id": str(uuid4()),
            "user_id": user_id,
            "type": alert_type,
            "source": source,
            "status": "active",
            "message": message,
            "location": location,
            "accuracy": accuracy,
            "battery": battery,
            "created_at": _now(),
        }
        self.alerts[alert["id"]] = alert
        self.event_log.append({"event": "alert_created", "alert_id": alert["id"], "created_at": _now()})
        return deepcopy(alert)

    def list_alerts(self) -> list[dict[str, Any]]:
        return sorted((deepcopy(alert) for alert in self.alerts.values()), key=lambda item: item["created_at"], reverse=True)

    def create_zone(
        self,
        *,
        name: str,
        description: str | None,
        severity: str,
        active: bool,
        geometry: dict[str, Any],
        created_by: str | None,
    ) -> dict[str, Any]:
        zone = {
            "id": str(uuid4()),
            "name": name,
            "description": description,
            "severity": severity,
            "active": active,
            "geometry": geometry,
            "created_by": created_by,
            "created_at": _now(),
        }
        self.zones[zone["id"]] = zone
        return deepcopy(zone)

    def update_zone(self, zone_id: str, **updates: Any) -> dict[str, Any]:
        zone = self.zones[zone_id]
        zone.update({key: value for key, value in updates.items() if value is not None})
        return deepcopy(zone)

    def list_zones(self) -> list[dict[str, Any]]:
        return [deepcopy(zone) for zone in self.zones.values() if zone.get("active")]

    def upsert_route(
        self,
        *,
        user_id: str,
        name: str,
        destination: str | None,
        expected_arrival: datetime | None,
        points: list[dict[str, float]],
        active: bool,
    ) -> dict[str, Any]:
        existing = next((route for route in self.routes.values() if route["user_id"] == user_id and route["name"] == name), None)
        if existing is None:
            existing = {
                "id": str(uuid4()),
                "user_id": user_id,
                "name": name,
                "destination": destination,
                "expected_arrival": expected_arrival,
                "points": points,
                "active": active,
                "created_at": _now(),
            }
            self.routes[existing["id"]] = existing
        else:
            existing.update({"destination": destination, "expected_arrival": expected_arrival, "points": points, "active": active})
        return deepcopy(existing)

    def get_route(self, user_id: str) -> dict[str, Any] | None:
        route = next((item for item in self.routes.values() if item["user_id"] == user_id and item.get("active")), None)
        return deepcopy(route) if route else None

    def register_responder(self, *, name: str, phone: str, region: str | None, device_token: str | None) -> dict[str, Any]:
        responder = {
            "id": str(uuid4()),
            "name": name,
            "phone": phone,
            "region": region,
            "device_token": device_token,
            "active": True,
            "created_at": _now(),
        }
        self.responders[responder["id"]] = responder
        return deepcopy(responder)

    def list_responders(self) -> list[dict[str, Any]]:
        return [deepcopy(responder) for responder in self.responders.values() if responder.get("active")]

    def log_notification(self, alert_id: str, **payload: Any) -> dict[str, Any]:
        notification = {
            "id": str(uuid4()),
            "alert_id": alert_id,
            "created_at": _now(),
            **payload,
        }
        self.notifications[notification["id"]] = notification
        return deepcopy(notification)


STORE = InMemoryStore()
