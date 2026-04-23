# Research Watcher + Arbitrage Simulation Platform

This repository now includes two components:

1. **Research watcher** for public market data polling and alert generation.
2. **Simulated arbitrage SaaS API** with multi-user allocations, centralized execution, PnL distribution, and platform revenue tracking.

## Arbitrage simulation API (Phase 1 + Phase 2)

### Features

- API-key based authentication for user endpoints.
- Per-user capital allocation.
- Centralized engine-only trade execution (users cannot trigger trades).
- Profit/loss distribution by allocation share.
- 20% performance fee on profitable user allocations.
- Compounding balances after each trade.
- Platform revenue tracking from collected fees.
- Background scanner/execution loop.
- Simulation-only execution mode (`EXECUTION_MODE=sim`) with latency, tx ids, and occasional failures.

### Endpoints

- `POST /user/create`
- `POST /allocate` (`x-api-key` required)
- `GET /dashboard` (`x-api-key` required)
- `GET /my/trades` (`x-api-key` required)
- `GET /metrics/revenue`
- `GET /metrics/live`

### Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn research_watcher.api:app --reload
```

Optional environment variables:

- `EXECUTION_MODE` (default: `sim`)
- `DB_PATH` (default: `simulation.db`)

## Existing research watcher

The original market-data research watcher modules are still present and tested (`research_watcher/main.py`, `research_watcher/exchanges.py`, `research_watcher/rules.py`).

## Codex workspace/profile setup (recommended)

If you use Codex across multiple repositories, avoid rebuilding local environments for each repo.

- Keep a single global Codex install and login.
- Put shared defaults in `~/.codex/config.toml`.
- Use project overrides in `.codex/config.toml` when needed.
- Define per-target profiles and switch with `codex --profile <name>`.
- Keep related repositories in one workspace tree (for example sibling folders under one directory).

Example:

```toml
# ~/.codex/config.toml
model = "gpt-5.4"
approval_policy = "on-request"

[profiles.overandor]
approval_policy = "on-request"

[profiles.jskroby]
approval_policy = "on-request"
```

```bash
codex --profile overandor
codex --profile jskroby
```
