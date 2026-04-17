from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_state(path: str) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def save_state(path: str, state: dict[str, Any]) -> None:
    p = Path(path)
    p.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
