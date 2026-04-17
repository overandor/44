from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(slots=True)
class WatcherConfig:
    symbol_gate: str = os.getenv("SYMBOL_GATE", "BTC_USDT")
    symbol_binance: str = os.getenv("SYMBOL_BINANCE", "BTCUSDT")
    funding_abs_threshold: float = float(os.getenv("FUNDING_ABS_THRESHOLD", "0.0008"))
    oi_jump_ratio_threshold: float = float(os.getenv("OI_JUMP_RATIO_THRESHOLD", "0.05"))
    spread_bps_threshold: float = float(os.getenv("SPREAD_BPS_THRESHOLD", "8"))
    state_file: str = os.getenv("STATE_FILE", ".watcher_state.json")
    github_repo: str = os.getenv("GITHUB_REPOSITORY", "")
    github_token: str = os.getenv("GITHUB_TOKEN", "")
