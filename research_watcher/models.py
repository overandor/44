from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class MarketSnapshot:
    venue: str
    symbol: str
    last_price: float
    funding_rate: float | None
    open_interest: float | None
    bid: float | None
    ask: float | None
    timestamp: datetime


@dataclass(slots=True)
class Alert:
    key: str
    title: str
    body: str
    severity: str
