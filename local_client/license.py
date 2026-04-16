from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import platform
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx

API_URL = os.getenv("LICENSE_API_URL", "http://127.0.0.1:8080/v1/license/check")
API_TOKEN = os.getenv("LICENSE_API_TOKEN", "dev-token-change-me")
SIGNING_SECRET = os.getenv("LICENSE_SIGNING_SECRET", "dev-signing-secret")
CACHE_PATH = Path(os.getenv("LICENSE_CACHE_PATH", ".license_cache.json"))


def machine_hash() -> str:
    raw = f"{platform.node()}::{platform.system()}::{platform.machine()}"
    return hashlib.sha256(raw.encode()).hexdigest()


def _verify_signed_grant(payload: dict[str, Any]) -> bool:
    grant = payload.get("grant")
    if not grant:
        return False

    body = base64.urlsafe_b64decode(grant["payload"].encode())
    expected = hmac.new(SIGNING_SECRET.encode(), body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, grant["signature"]):
        return False

    decoded = json.loads(body.decode())
    grace_until = decoded.get("grace_until")
    if grace_until and datetime.now(UTC) > datetime.fromisoformat(grace_until):
        return False

    return True


def _read_cache() -> dict[str, Any] | None:
    if not CACHE_PATH.exists():
        return None
    return json.loads(CACHE_PATH.read_text())


def _write_cache(data: dict[str, Any]) -> None:
    CACHE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def check_license(license_key: str, app_version: str) -> dict[str, Any]:
    payload = {
        "license_key": license_key,
        "machine_hash": machine_hash(),
        "app_version": app_version,
    }
    headers = {"x-api-token": API_TOKEN}

    try:
        with httpx.Client(timeout=8.0) as client:
            response = client.post(API_URL, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
        if data.get("allow") and not _verify_signed_grant(data):
            raise ValueError("invalid signed grant")
        _write_cache(data)
        return data
    except Exception as exc:
        cached = _read_cache()
        if cached and _verify_signed_grant(cached):
            cached["warning"] = f"offline mode: {exc}"
            return cached
        raise


def is_feature_enabled(feature: str) -> bool:
    data = _read_cache()
    if not data:
        return False
    return bool(data.get("allow")) and feature in data.get("features", [])


if __name__ == "__main__":
    key = os.getenv("LICENSE_KEY", "DEV-FREE-001")
    result = check_license(license_key=key, app_version="0.2.0")
    print("License check:", result)
    print("Auto-edit enabled:", is_feature_enabled("auto_edit"))
