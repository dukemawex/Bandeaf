from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.core.deps import create_access_token
from app.schemas.api import LoginRequest, RegisterRequest, TokenResponse, UserRead
from app.services.store import STORE

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead)
def register(payload: RegisterRequest):
    try:
        user = STORE.create_user(
            name=payload.name,
            phone=payload.phone,
            password=payload.password,
            region=payload.region,
            emergency_contacts=payload.emergency_contacts,
            checkin_interval=payload.checkin_interval,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return user


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest):
    user = STORE.authenticate(payload.phone, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(user["id"], extra={"is_admin": user.get("is_admin", False)})
    return TokenResponse(access_token=token)
