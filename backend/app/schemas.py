from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


Plan = Literal["free", "pro", "team"]
Status = Literal["active", "blocked", "expired"]


class LicenseCheckRequest(BaseModel):
    license_key: str = Field(min_length=3)
    machine_hash: str = Field(min_length=12)
    app_version: str = Field(min_length=1)


class SignedGrant(BaseModel):
    payload: str
    signature: str


class LicenseCheckResponse(BaseModel):
    allow: bool
    plan: Plan
    features: list[str]
    expires_at: datetime | None
    grace_until: datetime | None
    reason: str | None = None
    grant: SignedGrant | None = None


class LicenseRecord(BaseModel):
    key: str
    status: Status
    plan: Plan
    features: list[str]
    expires_at: datetime | None
    max_machines: int = 1
    bound_machines: list[str] = Field(default_factory=list)
