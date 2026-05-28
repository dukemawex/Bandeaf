#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import hmac
import json
import os
from datetime import datetime, timezone

import msgpack
import requests

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api/v1/alert/mesh-gateway")
HMAC_SECRET = os.getenv("MESH_GATEWAY_HMAC_SECRET", "change-me")


def build_signature(payload: dict) -> str:
    body = json.dumps(payload).encode("utf-8")
    return hmac.new(HMAC_SECRET.encode("utf-8"), body, hashlib.sha256).hexdigest()


def forward_payload(payload: dict) -> requests.Response:
    signature = build_signature(payload)
    return requests.post(BACKEND_URL, json=payload, headers={"X-HMAC-Signature": signature}, timeout=10)


def parse_meshtastic_packet(binary_payload: bytes) -> dict:
    data = msgpack.unpackb(binary_payload, raw=False)
    return {
        "uid": data.get("uid"),
        "lat": data.get("lat"),
        "lon": data.get("lon"),
        "type": data.get("type", "SOS"),
        "ts": data.get("ts") or datetime.now(tz=timezone.utc).isoformat(),
    }


def main() -> None:
    print("SAFE-NET mesh gateway service started")
    print("Bind this script to meshtastic-python receive callbacks in production.")


if __name__ == "__main__":
    main()
