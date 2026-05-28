from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status

from app.core.config import settings
from app.core.deps import get_current_admin, get_current_user, validate_hmac_signature
from app.schemas.api import AlertCreate, CheckinRequest, MeshAlertRequest, SmsInboundRequest
from app.services.geo import geojson_point
from app.services.notifications import build_help_message, notify_community_responders, notify_emergency_contacts
from app.services.store import STORE
from app.tasks.jobs import task_notify_community_responders, task_notify_emergency_contacts

router = APIRouter(prefix="/alert", tags=["alerts"])


@router.post("/sos")
def create_sos(payload: AlertCreate, user: dict[str, Any] = Depends(get_current_user)):
    location = None
    accuracy = payload.gps_coords.accuracy if payload.gps_coords else None
    if payload.gps_coords:
        location = geojson_point(payload.gps_coords.lat, payload.gps_coords.lon)
    alert = STORE.create_alert(
        user_id=user["id"],
        alert_type=payload.alert_type,
        source="app",
        location=location,
        accuracy=accuracy,
        battery=payload.battery_level,
        message=payload.message,
    )
    try:
        task_notify_emergency_contacts.delay(alert["id"])
        task_notify_community_responders.delay(alert["id"])
    except Exception:
        notify_emergency_contacts(alert)
        notify_community_responders(alert)
    return {"alert_id": alert["id"], "received_at": alert["created_at"], "status": alert["status"]}


@router.post("/checkin")
def checkin(payload: CheckinRequest, user: dict[str, Any] = Depends(get_current_user)):
    seen_at = payload.timestamp or datetime.now(tz=timezone.utc)
    updated = STORE.update_last_seen(user["id"], seen_at)
    due = updated["last_seen"].timestamp() + int(updated.get("checkin_interval") or 3600)
    return {"next_checkin_due": datetime.fromtimestamp(due, tz=timezone.utc)}


@router.post("/mesh-gateway")
async def ingest_mesh_gateway(request: Request, payload: MeshAlertRequest, x_hmac_signature: str = Header(..., alias="X-HMAC-Signature")):
    raw_body = await request.body()
    validate_hmac_signature(raw_body, x_hmac_signature, settings.MESH_GATEWAY_HMAC_SECRET)
    user = STORE.get_user(payload.uid)
    location = geojson_point(payload.lat, payload.lon) if payload.lat is not None and payload.lon is not None else None
    alert_type = "SOS" if payload.type in {"SOS", "ZONE_ALERT"} else "MISSED_CHECKIN"
    source = "mesh"
    alert = STORE.create_alert(
        user_id=user["id"] if user else None,
        alert_type=alert_type,
        source=source,
        location=location,
        battery=payload.battery_level,
        message=payload.message,
    )
    notify_emergency_contacts(alert)
    notify_community_responders(alert)
    return {"alert_id": alert["id"], "status": alert["status"]}


@router.post("/sms-inbound")
async def sms_inbound(request: Request, payload: SmsInboundRequest, x_hmac_signature: str = Header(..., alias="X-HMAC-Signature")):
    raw_body = await request.body()
    validate_hmac_signature(raw_body, x_hmac_signature, settings.MESH_GATEWAY_HMAC_SECRET)
    text = payload.text.strip()
    upper = text.upper()
    user = STORE.get_user_by_phone(payload.from_phone)

    if upper.startswith("JOIN"):
        parts = text.split(maxsplit=2)
        if len(parts) < 3:
            raise HTTPException(status_code=400, detail="JOIN format: JOIN [name] [region]")
        name_region = parts[1:]
        name = name_region[0]
        region = name_region[1] if len(name_region) > 1 else payload.region
        if user:
            return {"status": "already_registered"}
        STORE.create_user(name=name, phone=payload.from_phone, password="sms-user", region=region)
        return {"status": "registered"}

    if upper.startswith("SOS"):
        if not user:
            raise HTTPException(status_code=404, detail="User not registered")
        alert = STORE.create_alert(user_id=user["id"], alert_type="SOS", source="sms", message=text)
        notify_emergency_contacts(alert)
        notify_community_responders(alert)
        return {"status": "alerted", "alert_id": alert["id"]}

    if upper == "OK":
        if not user:
            raise HTTPException(status_code=404, detail="User not registered")
        STORE.update_last_seen(user["id"])
        return {"status": "checkin_reset"}

    if upper.startswith("ROUTE"):
        if not user:
            raise HTTPException(status_code=404, detail="User not registered")
        destination = text[5:].strip() or "Unknown"
        route = STORE.upsert_route(
            user_id=user["id"],
            name="SMS_ROUTE",
            destination=destination,
            expected_arrival=None,
            points=[],
            active=True,
        )
        return {"status": "route_logged", "route_id": route["id"]}

    if upper == "HELP":
        return {"status": "help", "message": build_help_message()}

    raise HTTPException(status_code=400, detail="Unsupported SMS keyword")


@router.get("/alerts")
def list_alerts(page: int = 1, page_size: int = 50, _: dict[str, Any] = Depends(get_current_admin)):
    alerts = STORE.list_alerts()
    start = max(page - 1, 0) * page_size
    end = start + page_size
    return {"items": alerts[start:end], "total": len(alerts), "page": page, "page_size": page_size}


@router.patch("/alerts/{alert_id}/status")
def update_alert_status(alert_id: str, status_value: str, _: dict[str, Any] = Depends(get_current_user)):
    alert = STORE.alerts.get(alert_id)
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    if status_value not in {"active", "acknowledged", "resolved"}:
        raise HTTPException(status_code=400, detail="Invalid status")
    alert["status"] = status_value
    STORE.event_log.append({"event": "alert_status", "alert_id": alert_id, "status": status_value, "created_at": datetime.now(tz=timezone.utc)})
    return {"id": alert_id, "status": status_value}
