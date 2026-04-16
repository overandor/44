from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

from backend.app.config import Settings
from backend.app.schemas import LicenseCheckRequest
from backend.app.service import LicenseService
from backend.app.store import LicenseStore


def test_unknown_key_returns_denied(tmp_path: Path) -> None:
    store = LicenseStore(path=tmp_path / "licenses.json")
    service = LicenseService(store=store, settings=Settings())

    result = service.check(
        LicenseCheckRequest(
            license_key="MISSING-KEY",
            machine_hash="x" * 32,
            app_version="0.2.0",
        )
    )

    assert result.allow is False
    assert result.reason == "unknown license key"


def test_machine_seat_limit(tmp_path: Path) -> None:
    store = LicenseStore(path=tmp_path / "licenses.json")
    service = LicenseService(store=store, settings=Settings())
    key = "DEV-FREE-001"

    first = service.check(
        LicenseCheckRequest(license_key=key, machine_hash="a" * 32, app_version="0.2.0")
    )
    second = service.check(
        LicenseCheckRequest(license_key=key, machine_hash="b" * 32, app_version="0.2.0")
    )

    assert first.allow is True
    assert second.allow is False
    assert second.reason == "seat limit reached"


def test_expired_license_denied(tmp_path: Path) -> None:
    store = LicenseStore(path=tmp_path / "licenses.json")
    record = store.get("DEV-PRO-123")
    assert record is not None
    record.expires_at = datetime.now(UTC) - timedelta(days=1)
    store.save(record)

    service = LicenseService(store=store, settings=Settings())
    result = service.check(
        LicenseCheckRequest(license_key="DEV-PRO-123", machine_hash="a" * 32, app_version="0.2.0")
    )

    assert result.allow is False
    assert result.reason == "license expired"
