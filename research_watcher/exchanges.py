from __future__ import annotations

from datetime import UTC, datetime

import httpx

from .models import MarketSnapshot

GATE_BASE = "https://api.gateio.ws/api/v4"
BINANCE_FAPI = "https://fapi.binance.com"


def fetch_gate_snapshot(symbol: str) -> MarketSnapshot:
    with httpx.Client(timeout=15.0) as client:
        ticker = client.get(f"{GATE_BASE}/futures/usdt/tickers", params={"contract": symbol}).json()[0]
        contract = client.get(f"{GATE_BASE}/futures/usdt/contracts/{symbol}").json()
        book = client.get(f"{GATE_BASE}/futures/usdt/order_book", params={"contract": symbol, "limit": 1}).json()

    bid = float(book["bids"][0][0]) if book.get("bids") else None
    ask = float(book["asks"][0][0]) if book.get("asks") else None

    return MarketSnapshot(
        venue="gate",
        symbol=symbol,
        last_price=float(ticker["last"]),
        funding_rate=float(contract.get("funding_rate") or 0.0),
        open_interest=float(ticker.get("total_size") or 0.0),
        bid=bid,
        ask=ask,
        timestamp=datetime.now(UTC),
    )


def fetch_binance_snapshot(symbol: str) -> MarketSnapshot:
    with httpx.Client(timeout=15.0) as client:
        ticker = client.get(f"{BINANCE_FAPI}/fapi/v1/ticker/24hr", params={"symbol": symbol}).json()
        premium = client.get(f"{BINANCE_FAPI}/fapi/v1/premiumIndex", params={"symbol": symbol}).json()
        oi = client.get(f"{BINANCE_FAPI}/fapi/v1/openInterest", params={"symbol": symbol}).json()
        book = client.get(f"{BINANCE_FAPI}/fapi/v1/depth", params={"symbol": symbol, "limit": 5}).json()

    bid = float(book["bids"][0][0]) if book.get("bids") else None
    ask = float(book["asks"][0][0]) if book.get("asks") else None

    return MarketSnapshot(
        venue="binance",
        symbol=symbol,
        last_price=float(ticker["lastPrice"]),
        funding_rate=float(premium.get("lastFundingRate") or 0.0),
        open_interest=float(oi.get("openInterest") or 0.0),
        bid=bid,
        ask=ask,
        timestamp=datetime.now(UTC),
    )
