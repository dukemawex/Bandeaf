from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.deps import get_current_admin
from app.services.store import STORE

router = APIRouter(prefix="/users", tags=["users"])


@router.get("")
def list_users(page: int = 1, page_size: int = 50, _admin=Depends(get_current_admin)):
    users = STORE.list_users()
    start = max(page - 1, 0) * page_size
    end = start + page_size
    return {"items": users[start:end], "total": len(users), "page": page, "page_size": page_size}
