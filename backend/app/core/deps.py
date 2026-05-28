from __future__ import annotations

import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.core.config import settings
from app.services.store import STORE


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")


def utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


def create_access_token(subject: str, expires_delta: timedelta | None = None, extra: dict[str, Any] | None = None) -> str:
    expire = utcnow() + (expires_delta or timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES))
    payload: dict[str, Any] = {"sub": subject, "exp": expire}
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token") from exc


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict[str, Any]:
    payload = decode_access_token(token)
    user = STORE.get_user(payload.get("sub"))
    if not user or not user.get("is_active"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return user


def get_current_admin(user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    if not user.get("is_admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return user


def validate_hmac_signature(raw_body: bytes, signature: str, secret: str) -> None:
    expected = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature.strip()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid HMAC signature")


def verify_mesh_hmac(x_hmac_signature: str = Header(..., alias="X-HMAC-Signature"), raw_body: bytes = b"") -> None:
    validate_hmac_signature(raw_body, x_hmac_signature, settings.MESH_GATEWAY_HMAC_SECRET)
