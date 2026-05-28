from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.core.deps import get_current_admin
from app.schemas.api import DangerZoneRequest
from app.services.geo import geojson_polygon
from app.services.store import STORE

router = APIRouter(prefix="/zones", tags=["zones"])


@router.get("/danger")
def list_danger_zones() -> dict[str, Any]:
    zones = STORE.list_zones()
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "id": zone["id"],
                "geometry": zone["geometry"],
                "properties": {
                    "name": zone["name"],
                    "description": zone.get("description"),
                    "severity": zone["severity"],
                    "active": zone["active"],
                },
            }
            for zone in zones
        ],
    }


@router.post("/danger")
def create_danger_zone(payload: DangerZoneRequest, admin: dict[str, Any] = Depends(get_current_admin)):
    if not payload.coordinates:
        raise HTTPException(status_code=400, detail="Zone coordinates required")
    zone = STORE.create_zone(
        name=payload.name,
        description=payload.description,
        severity=payload.severity,
        active=payload.active,
        geometry=geojson_polygon(payload.coordinates),
        created_by=admin["id"],
    )
    return zone


@router.put("/danger/{zone_id}")
def update_danger_zone(zone_id: str, payload: DangerZoneRequest, _: dict[str, Any] = Depends(get_current_admin)):
    if zone_id not in STORE.zones:
        raise HTTPException(status_code=404, detail="Zone not found")
    zone = STORE.update_zone(
        zone_id,
        name=payload.name,
        description=payload.description,
        severity=payload.severity,
        active=payload.active,
        geometry=geojson_polygon(payload.coordinates),
    )
    return zone
