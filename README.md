# Research Watcher (Gate.io + Binance, no API key)

This repo now includes a **public market-data research watcher** that polls Gate.io and Binance perpetual futures endpoints and opens/updates GitHub issues as research alerts.

## What it does

- Polls Gate.io USDT perpetual data (ticker, contract funding fields, order book).
- Polls Binance USDⓈ-M futures data (24hr ticker, premium index/funding, open interest, depth).
- Evaluates alert rules:
  - funding-rate extremes,
  - open-interest jumps,
  - spread widening.
- Upserts GitHub issues with `research-alert` labels.
- Runs in GitHub Actions every 15 minutes.

## Endpoints used

### Gate.io (public)
- `GET https://api.gateio.ws/api/v4/futures/usdt/tickers?contract=BTC_USDT`
- `GET https://api.gateio.ws/api/v4/futures/usdt/contracts/BTC_USDT`
- `GET https://api.gateio.ws/api/v4/futures/usdt/order_book?contract=BTC_USDT&limit=1`

### Binance USDⓈ-M (public)
- `GET https://fapi.binance.com/fapi/v1/ticker/24hr?symbol=BTCUSDT`
- `GET https://fapi.binance.com/fapi/v1/premiumIndex?symbol=BTCUSDT`
- `GET https://fapi.binance.com/fapi/v1/openInterest?symbol=BTCUSDT`
- `GET https://fapi.binance.com/fapi/v1/depth?symbol=BTCUSDT&limit=5`

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m research_watcher.main
```

Optional env vars:

- `SYMBOL_GATE` (default `BTC_USDT`)
- `SYMBOL_BINANCE` (default `BTCUSDT`)
- `FUNDING_ABS_THRESHOLD` (default `0.0008`)
- `OI_JUMP_RATIO_THRESHOLD` (default `0.05`)
- `SPREAD_BPS_THRESHOLD` (default `8`)
- `STATE_FILE` (default `.watcher_state.json`)
- `GITHUB_TOKEN`, `GITHUB_REPOSITORY` (for issue creation/updating)

## GitHub Actions

Workflow: `.github/workflows/research-watcher.yml`

- Runs every 15 minutes via cron.
- Uses `secrets.GITHUB_TOKEN` and repo permissions `issues: write`.

## Project layout

```text
research_watcher/
  config.py
  exchanges.py
  github_issues.py
  main.py
  models.py
  rules.py
  state.py
tests/
  test_rules.py
.github/workflows/research-watcher.yml
```
