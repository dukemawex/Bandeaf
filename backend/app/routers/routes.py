from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.core.deps import get_current_user
from app.schemas.api import RouteUpsertRequest
from app.services.store import STORE

router = APIRouter(prefix="/user/route", tags=["routes"])


@router.get("")
def get_route(user: dict[str, Any] = Depends(get_current_user)):
    route = STORE.get_route(user["id"])
    if not route:
        raise HTTPException(status_code=404, detail="No active route")
    return route


@router.post("")
def upsert_route(payload: RouteUpsertRequest, user: dict[str, Any] = Depends(get_current_user)):
    route = STORE.upsert_route(
        user_id=user["id"],
        name=payload.name,
        destination=payload.destination,
        expected_arrival=payload.expected_arrival,
        points=[point.model_dump() for point in payload.points],
        active=payload.active,
    )
    return route
