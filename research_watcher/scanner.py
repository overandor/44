from __future__ import annotations

import random
from datetime import UTC, datetime


class OpportunityScanner:
    def find_opportunity(self) -> dict[str, str] | None:
        # Centralized, internal-only: never exposed via API.
        if random.random() < 0.55:
            return {
                "id": f"opp-{random.randint(1000, 9999)}",
                "detected_at": datetime.now(UTC).isoformat(),
            }
        return None
