from __future__ import annotations

import hashlib
import hmac
import json

from app.core.config import settings
from app.services.store import STORE


def _auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def build_hmac(payload: dict) -> str:
    raw = json.dumps(payload).encode("utf-8")
    return hmac.new(settings.MESH_GATEWAY_HMAC_SECRET.encode("utf-8"), raw, hashlib.sha256).hexdigest()


def test_health(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_register_and_login(client):
    register = client.post(
        "/api/v1/auth/register",
        json={"name": "Bob", "phone": "+333", "password": "secret123", "region": "west", "emergency_contacts": []},
    )
    assert register.status_code == 200

    login = client.post("/api/v1/auth/login", json={"phone": "+333", "password": "secret123"})
    assert login.status_code == 200
    assert login.json()["access_token"]


def test_sos_checkin_and_route_flow(client, user_token):
    sos = client.post(
        "/api/v1/alert/sos",
        headers=_auth_header(user_token),
        json={"gps_coords": {"lat": 6.45, "lon": 3.4, "accuracy": 10}, "battery_level": 80, "alert_type": "SOS"},
    )
    assert sos.status_code == 200
    assert sos.json()["status"] == "active"

    checkin = client.post("/api/v1/alert/checkin", headers=_auth_header(user_token), json={})
    assert checkin.status_code == 200
    assert "next_checkin_due" in checkin.json()

    upsert = client.post(
        "/api/v1/user/route",
        headers=_auth_header(user_token),
        json={"name": "Commute", "destination": "Village", "points": [{"lat": 6.4, "lon": 3.3}], "active": True},
    )
    assert upsert.status_code == 200

    get_route = client.get("/api/v1/user/route", headers=_auth_header(user_token))
    assert get_route.status_code == 200
    assert get_route.json()["name"] == "Commute"


def test_mesh_gateway_ingest(client, admin_user):
    payload = {"uid": admin_user["id"], "lat": 6.3, "lon": 3.2, "type": "SOS"}
    signature = build_hmac(payload)
    response = client.post("/api/v1/alert/mesh-gateway", headers={"X-HMAC-Signature": signature}, json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "active"


def test_sms_inbound_keywords(client, standard_user):
    payload = {"from_phone": standard_user["phone"], "text": "HELP", "region": "forest"}
    signature = build_hmac(payload)
    help_resp = client.post("/api/v1/alert/sms-inbound", headers={"X-HMAC-Signature": signature}, json=payload)
    assert help_resp.status_code == 200
    assert help_resp.json()["status"] == "help"

    sos_payload = {"from_phone": standard_user["phone"], "text": "SOS Alice", "region": "forest"}
    sos_sig = build_hmac(sos_payload)
    sos_resp = client.post("/api/v1/alert/sms-inbound", headers={"X-HMAC-Signature": sos_sig}, json=sos_payload)
    assert sos_resp.status_code == 200
    assert sos_resp.json()["status"] == "alerted"


def test_zone_user_responder_admin_endpoints(client, admin_token):
    zone = {
        "name": "Hotspot",
        "description": "Recent attacks",
        "severity": "high",
        "active": True,
        "coordinates": [[[3.2, 6.2], [3.4, 6.2], [3.4, 6.4], [3.2, 6.2]]],
    }
    create_zone = client.post("/api/v1/zones/danger", headers=_auth_header(admin_token), json=zone)
    assert create_zone.status_code == 200

    list_zone = client.get("/api/v1/zones/danger")
    assert list_zone.status_code == 200
    assert list_zone.json()["type"] == "FeatureCollection"

    responder = client.post(
        "/api/v1/responders",
        headers=_auth_header(admin_token),
        json={"name": "R1", "phone": "+444", "region": "north", "device_token": "abc"},
    )
    assert responder.status_code == 200

    users = client.get("/api/v1/users", headers=_auth_header(admin_token))
    assert users.status_code == 200
    assert users.json()["total"] >= 1


def test_alert_list_and_status_update(client, admin_token, user_token):
    create = client.post(
        "/api/v1/alert/sos",
        headers=_auth_header(user_token),
        json={"gps_coords": {"lat": 1.0, "lon": 2.0}, "alert_type": "SOS"},
    )
    alert_id = create.json()["alert_id"]

    listing = client.get("/api/v1/alert/alerts", headers=_auth_header(admin_token))
    assert listing.status_code == 200
    assert listing.json()["total"] >= 1

    update = client.patch(f"/api/v1/alert/alerts/{alert_id}/status", headers=_auth_header(user_token), params={"status_value": "acknowledged"})
    assert update.status_code == 200
    assert STORE.alerts[alert_id]["status"] == "acknowledged"
