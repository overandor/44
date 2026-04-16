from __future__ import annotations

import base64
import hashlib
import hmac
import json
from typing import Any

from .schemas import SignedGrant


def sign_payload(payload: dict[str, Any], secret: str) -> SignedGrant:
    body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
    encoded = base64.urlsafe_b64encode(body).decode()
    signature = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return SignedGrant(payload=encoded, signature=signature)


def verify_grant(grant: SignedGrant, secret: str) -> dict[str, Any] | None:
    try:
        body = base64.urlsafe_b64decode(grant.payload.encode())
    except Exception:
        return None

    expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, grant.signature):
        return None
    return json.loads(body.decode())
