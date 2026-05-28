from __future__ import annotations

import hashlib
import hmac
import json
import sys
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import settings
from app.core.deps import create_access_token
from app.main import app
from app.services.store import STORE


@pytest.fixture(autouse=True)
def reset_store() -> None:
    STORE.reset()


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture()
def admin_user() -> dict[str, Any]:
    return STORE.create_user(name="Admin", phone="+111", password="admin-pass", region="north", is_admin=True)


@pytest.fixture()
def standard_user() -> dict[str, Any]:
    return STORE.create_user(name="Alice", phone="+222", password="user-pass", region="forest")


@pytest.fixture()
def admin_token(admin_user: dict[str, Any]) -> str:
    return create_access_token(admin_user["id"], extra={"is_admin": True})


@pytest.fixture()
def user_token(standard_user: dict[str, Any]) -> str:
    return create_access_token(standard_user["id"], extra={"is_admin": False})


def build_hmac(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload).encode("utf-8")
    return hmac.new(settings.MESH_GATEWAY_HMAC_SECRET.encode("utf-8"), raw, hashlib.sha256).hexdigest()
