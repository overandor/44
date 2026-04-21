from __future__ import annotations

import asyncio
import random
import uuid
from dataclasses import dataclass

from .db import Database


@dataclass(slots=True)
class TradeResult:
    id: int
    status: str
    actual_profit: float
    latency_ms: int
    tx_id: str
    reason: str = ""


class ExecutionEngine:
    def __init__(self, db: Database, execution_mode: str = "sim") -> None:
        self.db = db
        self.execution_mode = execution_mode

    async def execute_trade(self, opportunity: dict[str, str | float] | None = None) -> TradeResult:
        if self.execution_mode != "sim":
            raise RuntimeError("Only simulation mode is supported in this build")

        latency_ms = random.randint(50, 250)
        await asyncio.sleep(latency_ms / 1000)
        tx_id = f"sim-{uuid.uuid4().hex[:10]}"

        if random.random() < 0.08:
            trade_id = self.db.insert_trade(
                status="failed",
                actual_profit=0,
                latency_ms=latency_ms,
                tx_id=tx_id,
                reason="simulated execution failure",
            )
            return TradeResult(id=trade_id, status="failed", actual_profit=0, latency_ms=latency_ms, tx_id=tx_id)

        if random.random() < 0.65:
            actual_profit = float(random.randint(20_000, 120_000))
        else:
            actual_profit = float(-random.randint(5_000, 30_000))

        trade_id = self.db.insert_trade(
            status="success",
            actual_profit=actual_profit,
            latency_ms=latency_ms,
            tx_id=tx_id,
        )
        return TradeResult(
            id=trade_id,
            status="success",
            actual_profit=actual_profit,
            latency_ms=latency_ms,
            tx_id=tx_id,
        )

    async def execute_and_distribute(self, opportunity: dict[str, str | float] | None = None) -> TradeResult:
        result = await self.execute_trade(opportunity)
        if result.status != "success":
            return result

        total_capital = self.db.get_total_capital()
        if total_capital == 0:
            return result

        users = self.db.get_all_allocations()
        for user in users:
            share = user.capital / total_capital
            gross_profit = result.actual_profit * share
            fee = gross_profit * 0.20 if gross_profit > 0 else 0
            net_profit = gross_profit - fee
            self.db.insert_user_pnl(
                user_id=user.user_id,
                trade_id=result.id,
                profit=net_profit,
                fee=fee,
            )
            self.db.insert_platform_revenue(fee, result.id)
            self.db.update_user_balance(user.user_id, net_profit)
        return result
