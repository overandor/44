from __future__ import annotations

from .config import WatcherConfig
from .exchanges import fetch_binance_snapshot, fetch_gate_snapshot
from .github_issues import upsert_alert_issue
from .rules import evaluate_snapshot
from .state import load_state, save_state


def run() -> int:
    config = WatcherConfig()
    state = load_state(config.state_file)

    snapshots = [
        fetch_gate_snapshot(config.symbol_gate),
        fetch_binance_snapshot(config.symbol_binance),
    ]

    for snapshot in snapshots:
        state_key = f"{snapshot.venue}:{snapshot.symbol}"
        prev_oi = state.get(state_key, {}).get("open_interest")
        alerts = evaluate_snapshot(snapshot=snapshot, previous_open_interest=prev_oi, config=config)
        for alert in alerts:
            upsert_alert_issue(config.github_repo, config.github_token, alert)

        state[state_key] = {
            "open_interest": snapshot.open_interest,
            "last_price": snapshot.last_price,
            "timestamp": snapshot.timestamp.isoformat(),
        }

    save_state(config.state_file, state)
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
