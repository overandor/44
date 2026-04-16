from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

from .schemas import LicenseRecord

DB_PATH = Path("backend/data/licenses.json")


class LicenseStore:
    def __init__(self, path: Path = DB_PATH) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._seed()

    def _seed(self) -> None:
        now = datetime.now(UTC)
        sample = {
            "DEV-FREE-001": {
                "key": "DEV-FREE-001",
                "status": "active",
                "plan": "free",
                "features": ["basic_chat", "local_tts"],
                "expires_at": None,
                "max_machines": 1,
                "bound_machines": [],
            },
            "DEV-PRO-123": {
                "key": "DEV-PRO-123",
                "status": "active",
                "plan": "pro",
                "features": ["basic_chat", "local_tts", "auto_edit", "agents"],
                "expires_at": (now + timedelta(days=30)).isoformat(),
                "max_machines": 3,
                "bound_machines": [],
            },
            "DEV-BLOCKED-999": {
                "key": "DEV-BLOCKED-999",
                "status": "blocked",
                "plan": "pro",
                "features": ["basic_chat", "local_tts", "auto_edit", "agents"],
                "expires_at": (now + timedelta(days=365)).isoformat(),
                "max_machines": 1,
                "bound_machines": [],
            },
        }
        self.path.write_text(json.dumps(sample, indent=2), encoding="utf-8")

    def _read(self) -> dict:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _write(self, payload: dict) -> None:
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def get(self, key: str) -> LicenseRecord | None:
        data = self._read().get(key)
        if not data:
            return None
        return LicenseRecord(**data)

    def save(self, record: LicenseRecord) -> None:
        payload = self._read()
        item = record.model_dump(mode="json")
        payload[record.key] = item
        self._write(payload)
