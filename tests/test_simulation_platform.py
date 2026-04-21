from __future__ import annotations

import asyncio

from research_watcher.db import Database
from research_watcher.engine import ExecutionEngine, TradeResult


async def _run_distribute(db: Database, trade_profit: float) -> None:
    engine = ExecutionEngine(db=db, execution_mode="sim")

    async def fake_execute_trade(opportunity: dict[str, str] | None = None) -> TradeResult:
        trade_id = db.insert_trade("success", trade_profit, latency_ms=100, tx_id="sim-fixed")
        return TradeResult(
            id=trade_id,
            status="success",
            actual_profit=trade_profit,
            latency_ms=100,
            tx_id="sim-fixed",
        )

    engine.execute_trade = fake_execute_trade  # type: ignore[method-assign]
    await engine.execute_and_distribute({"id": "forced"})


def test_profit_distribution_and_fee(tmp_path) -> None:
    db = Database(str(tmp_path / "test.db"))
    u1 = db.create_user("alice", "k1")
    u2 = db.create_user("bob", "k2")
    db.set_allocation(u1.id, 1000)
    db.set_allocation(u2.id, 3000)

    asyncio.run(_run_distribute(db, 1000.0))

    # 25/75 split, then 20% fee on gains
    # user1 gross=250 fee=50 net=200 ; user2 gross=750 fee=150 net=600
    assert db.get_user_capital(u1.id) == 1200
    assert db.get_user_capital(u2.id) == 3600
    assert db.platform_revenue_total() == 200


def test_no_fee_on_loss(tmp_path) -> None:
    db = Database(str(tmp_path / "test.db"))
    u1 = db.create_user("alice", "k1")
    db.set_allocation(u1.id, 1000)

    asyncio.run(_run_distribute(db, -100.0))

    assert db.get_user_capital(u1.id) == 900
    assert db.platform_revenue_total() == 0
