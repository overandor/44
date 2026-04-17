from __future__ import annotations

from .config import WatcherConfig
from .models import Alert, MarketSnapshot


def _spread_bps(snapshot: MarketSnapshot) -> float | None:
    if snapshot.bid is None or snapshot.ask is None:
        return None
    mid = (snapshot.bid + snapshot.ask) / 2
    if mid == 0:
        return None
    return ((snapshot.ask - snapshot.bid) / mid) * 10_000


def evaluate_snapshot(
    snapshot: MarketSnapshot,
    previous_open_interest: float | None,
    config: WatcherConfig,
) -> list[Alert]:
    alerts: list[Alert] = []

    if snapshot.funding_rate is not None and abs(snapshot.funding_rate) >= config.funding_abs_threshold:
        alerts.append(
            Alert(
                key=f"{snapshot.venue}:{snapshot.symbol}:funding",
                severity="high",
                title=f"{snapshot.venue.upper()} {snapshot.symbol} funding extreme",
                body=(
                    f"Funding rate is {snapshot.funding_rate:.6f}, above threshold "
                    f"{config.funding_abs_threshold:.6f}."
                ),
            )
        )

    if previous_open_interest and snapshot.open_interest:
        oi_jump = (snapshot.open_interest - previous_open_interest) / previous_open_interest
        if abs(oi_jump) >= config.oi_jump_ratio_threshold:
            alerts.append(
                Alert(
                    key=f"{snapshot.venue}:{snapshot.symbol}:oi_jump",
                    severity="medium",
                    title=f"{snapshot.venue.upper()} {snapshot.symbol} open-interest jump",
                    body=(
                        f"Open interest moved by {oi_jump * 100:.2f}% "
                        f"(prev={previous_open_interest:.2f}, now={snapshot.open_interest:.2f})."
                    ),
                )
            )

    spread = _spread_bps(snapshot)
    if spread is not None and spread >= config.spread_bps_threshold:
        alerts.append(
            Alert(
                key=f"{snapshot.venue}:{snapshot.symbol}:spread",
                severity="medium",
                title=f"{snapshot.venue.upper()} {snapshot.symbol} spread widening",
                body=f"Bid/ask spread is {spread:.2f} bps (>={config.spread_bps_threshold:.2f} bps).",
            )
        )

    return alerts
