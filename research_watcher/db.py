from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class User:
    id: int
    api_key: str
    name: str
    created_at: str


@dataclass(slots=True)
class Allocation:
    user_id: int
    capital: float


class Database:
    def __init__(self, path: str = "simulation.db") -> None:
        self.path = path
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    api_key TEXT UNIQUE,
                    name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS allocations (
                    user_id INTEGER PRIMARY KEY,
                    capital REAL,
                    updated_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );
                CREATE TABLE IF NOT EXISTS user_pnl (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    trade_id INTEGER,
                    profit REAL,
                    fee REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS platform_revenue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    amount REAL,
                    trade_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    status TEXT,
                    actual_profit REAL,
                    latency_ms INTEGER,
                    tx_id TEXT,
                    reason TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

    def create_user(self, name: str, api_key: str) -> User:
        with self._connect() as conn:
            row = conn.execute(
                "INSERT INTO users(api_key, name) VALUES(?, ?) RETURNING *",
                (api_key, name),
            ).fetchone()
        return User(**dict(row))

    def get_user_by_key(self, api_key: str) -> User | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM users WHERE api_key = ?", (api_key,)).fetchone()
        return User(**dict(row)) if row else None

    def set_allocation(self, user_id: int, capital: float) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO allocations(user_id, capital, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id) DO UPDATE SET
                    capital=excluded.capital,
                    updated_at=CURRENT_TIMESTAMP
                """,
                (user_id, capital),
            )

    def get_user_capital(self, user_id: int) -> float:
        with self._connect() as conn:
            row = conn.execute("SELECT capital FROM allocations WHERE user_id = ?", (user_id,)).fetchone()
        return float(row["capital"]) if row else 0.0

    def update_user_balance(self, user_id: int, delta: float) -> None:
        current = self.get_user_capital(user_id)
        self.set_allocation(user_id, current + delta)

    def get_total_capital(self) -> float:
        with self._connect() as conn:
            row = conn.execute("SELECT COALESCE(SUM(capital), 0) AS total FROM allocations").fetchone()
        return float(row["total"])

    def get_all_allocations(self) -> list[Allocation]:
        with self._connect() as conn:
            rows = conn.execute("SELECT user_id, capital FROM allocations WHERE capital > 0").fetchall()
        return [Allocation(user_id=int(r["user_id"]), capital=float(r["capital"])) for r in rows]

    def insert_trade(self, status: str, actual_profit: float, latency_ms: int, tx_id: str, reason: str = "") -> int:
        with self._connect() as conn:
            row = conn.execute(
                """
                INSERT INTO trades(status, actual_profit, latency_ms, tx_id, reason)
                VALUES (?, ?, ?, ?, ?)
                RETURNING id
                """,
                (status, actual_profit, latency_ms, tx_id, reason),
            ).fetchone()
        return int(row["id"])

    def insert_user_pnl(self, user_id: int, trade_id: int, profit: float, fee: float) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO user_pnl(user_id, trade_id, profit, fee) VALUES (?, ?, ?, ?)",
                (user_id, trade_id, profit, fee),
            )

    def insert_platform_revenue(self, amount: float, trade_id: int) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO platform_revenue(amount, trade_id) VALUES (?, ?)",
                (amount, trade_id),
            )

    def user_dashboard(self, user_id: int) -> dict[str, float | int]:
        with self._connect() as conn:
            pnl_total = conn.execute(
                "SELECT COALESCE(SUM(profit), 0) AS value FROM user_pnl WHERE user_id = ?",
                (user_id,),
            ).fetchone()["value"]
            pnl_24h = conn.execute(
                """
                SELECT COALESCE(SUM(profit), 0) AS value
                FROM user_pnl
                WHERE user_id = ? AND created_at >= datetime('now', '-1 day')
                """,
                (user_id,),
            ).fetchone()["value"]
            fees = conn.execute(
                "SELECT COALESCE(SUM(fee), 0) AS value FROM user_pnl WHERE user_id = ?",
                (user_id,),
            ).fetchone()["value"]
            trades = conn.execute("SELECT COUNT(*) AS value FROM user_pnl WHERE user_id = ?", (user_id,)).fetchone()[
                "value"
            ]

        return {
            "capital": self.get_user_capital(user_id),
            "pnl_total": float(pnl_total),
            "pnl_24h": float(pnl_24h),
            "fees_paid": float(fees),
            "trades": int(trades),
        }

    def user_trades(self, user_id: int) -> list[dict[str, str | float | int]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT p.trade_id, p.profit, p.fee, p.created_at, t.status, t.latency_ms, t.tx_id
                FROM user_pnl p
                JOIN trades t ON t.id = p.trade_id
                WHERE p.user_id = ?
                ORDER BY p.id DESC
                """,
                (user_id,),
            ).fetchall()
        return [dict(r) for r in rows]

    def platform_revenue_total(self) -> float:
        with self._connect() as conn:
            row = conn.execute("SELECT COALESCE(SUM(amount), 0) AS value FROM platform_revenue").fetchone()
        return float(row["value"])

    def live_metrics(self) -> dict[str, float | int]:
        with self._connect() as conn:
            trade_count = int(conn.execute("SELECT COUNT(*) AS value FROM trades").fetchone()["value"])
            wins = int(conn.execute("SELECT COUNT(*) AS value FROM trades WHERE actual_profit > 0").fetchone()["value"])
            avg_latency = float(
                conn.execute("SELECT COALESCE(AVG(latency_ms), 0) AS value FROM trades WHERE status = 'success'").fetchone()[
                    "value"
                ]
            )
            rolling_pnl = float(
                conn.execute(
                    "SELECT COALESCE(SUM(actual_profit), 0) AS value FROM trades WHERE created_at >= datetime('now', '-1 hour')"
                ).fetchone()["value"]
            )
        win_rate = (wins / trade_count) if trade_count else 0.0
        return {
            "trade_count": trade_count,
            "win_rate": win_rate,
            "avg_latency_ms": avg_latency,
            "rolling_pnl": rolling_pnl,
            "platform_revenue": self.platform_revenue_total(),
        }
