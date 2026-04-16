from __future__ import annotations

from fastapi import FastAPI, Header, HTTPException

from backend.app.config import settings
from backend.app.schemas import LicenseCheckRequest, LicenseCheckResponse
from backend.app.service import LicenseService
from backend.app.store import LicenseStore

app = FastAPI(title="Local-First License API", version="0.2.0")
service = LicenseService(store=LicenseStore(), settings=settings)


def _check_auth(header_token: str | None) -> None:
    if header_token != settings.api_token:
        raise HTTPException(status_code=401, detail="invalid api token")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/license/check", response_model=LicenseCheckResponse)
def check_license(
    payload: LicenseCheckRequest,
    x_api_token: str | None = Header(default=None),
) -> LicenseCheckResponse:
    _check_auth(x_api_token)
    return service.check(payload)
