from __future__ import annotations

from datetime import UTC, datetime

from research_watcher.config import WatcherConfig
from research_watcher.models import MarketSnapshot
from research_watcher.rules import evaluate_snapshot


def test_funding_alert_triggered() -> None:
    cfg = WatcherConfig(funding_abs_threshold=0.0008)
    snap = MarketSnapshot(
        venue="binance",
        symbol="BTCUSDT",
        last_price=65000,
        funding_rate=0.0012,
        open_interest=1_000_000,
        bid=64999,
        ask=65001,
        timestamp=datetime.now(UTC),
    )

    alerts = evaluate_snapshot(snap, previous_open_interest=900_000, config=cfg)

    assert any(a.key.endswith(":funding") for a in alerts)


def test_oi_jump_alert_triggered() -> None:
    cfg = WatcherConfig(oi_jump_ratio_threshold=0.05)
    snap = MarketSnapshot(
        venue="gate",
        symbol="BTC_USDT",
        last_price=64000,
        funding_rate=0.0001,
        open_interest=1_100_000,
        bid=63999,
        ask=64001,
        timestamp=datetime.now(UTC),
    )

    alerts = evaluate_snapshot(snap, previous_open_interest=1_000_000, config=cfg)

    assert any(a.key.endswith(":oi_jump") for a in alerts)


def test_spread_alert_triggered() -> None:
    cfg = WatcherConfig(spread_bps_threshold=8)
    snap = MarketSnapshot(
        venue="gate",
        symbol="BTC_USDT",
        last_price=64000,
        funding_rate=0.0001,
        open_interest=1_000_000,
        bid=63950,
        ask=64050,
        timestamp=datetime.now(UTC),
    )

    alerts = evaluate_snapshot(snap, previous_open_interest=1_000_000, config=cfg)

    assert any(a.key.endswith(":spread") for a in alerts)
