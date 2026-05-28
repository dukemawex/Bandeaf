from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from app.core.deps import get_current_admin
from app.schemas.api import ResponderRequest
from app.services.store import STORE

router = APIRouter(prefix="/responders", tags=["responders"])


@router.get("")
def list_responders(admin: dict[str, Any] = Depends(get_current_admin)):
    _ = admin
    return STORE.list_responders()


@router.post("")
def register_responder(payload: ResponderRequest, admin: dict[str, Any] = Depends(get_current_admin)):
    _ = admin
    return STORE.register_responder(
        name=payload.name,
        phone=payload.phone,
        region=payload.region,
        device_token=payload.device_token,
    )
