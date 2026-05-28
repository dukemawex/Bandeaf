from __future__ import annotations

import asyncio
import json
from datetime import datetime

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.services.store import STORE

router = APIRouter(prefix="/stream", tags=["stream"])


def _serialize_event(event: dict) -> str:
    payload = {
        **event,
        "created_at": event.get("created_at").isoformat() if isinstance(event.get("created_at"), datetime) else event.get("created_at"),
    }
    return f"data: {json.dumps(payload)}\n\n"


@router.get("/alerts")
async def alert_stream() -> StreamingResponse:
    async def event_generator():
        cursor = 0
        while True:
            events = STORE.event_log[cursor:]
            for event in events:
                cursor += 1
                yield _serialize_event(event)
            await asyncio.sleep(1)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
