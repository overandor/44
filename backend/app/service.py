from __future__ import annotations

from datetime import UTC, datetime, timedelta

from .config import Settings
from .schemas import LicenseCheckRequest, LicenseCheckResponse, LicenseRecord
from .security import sign_payload
from .store import LicenseStore


class LicenseService:
    def __init__(self, store: LicenseStore, settings: Settings) -> None:
        self.store = store
        self.settings = settings

    def check(self, request: LicenseCheckRequest) -> LicenseCheckResponse:
        record = self.store.get(request.license_key)
        if record is None:
            return LicenseCheckResponse(
                allow=False,
                plan="free",
                features=["basic_chat"],
                expires_at=None,
                grace_until=None,
                reason="unknown license key",
            )

        now = datetime.now(UTC)
        if record.status != "active":
            return self._deny(record, reason=f"license status: {record.status}")

        if record.expires_at and now > record.expires_at:
            return self._deny(record, reason="license expired")

        if request.machine_hash not in record.bound_machines:
            if len(record.bound_machines) >= record.max_machines:
                return self._deny(record, reason="seat limit reached")
            record.bound_machines.append(request.machine_hash)
            self.store.save(record)

        grace_until = now + timedelta(hours=self.settings.default_grace_hours)
        grant = sign_payload(
            {
                "license_key": record.key,
                "plan": record.plan,
                "features": record.features,
                "expires_at": record.expires_at.isoformat() if record.expires_at else None,
                "grace_until": grace_until.isoformat(),
                "checked_at": now.isoformat(),
                "app_version": request.app_version,
            },
            self.settings.signing_secret,
        )
        return LicenseCheckResponse(
            allow=True,
            plan=record.plan,
            features=record.features,
            expires_at=record.expires_at,
            grace_until=grace_until,
            grant=grant,
        )

    @staticmethod
    def _deny(record: LicenseRecord, reason: str) -> LicenseCheckResponse:
        return LicenseCheckResponse(
            allow=False,
            plan=record.plan,
            features=record.features,
            expires_at=record.expires_at,
            grace_until=None,
            reason=reason,
        )
