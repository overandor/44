from __future__ import annotations

import asyncio
import os
import secrets
from contextlib import suppress

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from .db import Database, User
from .engine import ExecutionEngine
from .scanner import OpportunityScanner

EXECUTION_MODE = os.getenv("EXECUTION_MODE", "sim")
DB_PATH = os.getenv("DB_PATH", "simulation.db")

app = FastAPI(title="Arbitrage Simulation Platform", version="0.1.0")
db = Database(DB_PATH)
engine = ExecutionEngine(db=db, execution_mode=EXECUTION_MODE)
scanner = OpportunityScanner()


class CreateUserRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class AllocationRequest(BaseModel):
    capital: float = Field(ge=0)


async def execution_loop() -> None:
    while True:
        opp = scanner.find_opportunity()
        if opp:
            await engine.execute_and_distribute(opp)
        await asyncio.sleep(1)


@app.on_event("startup")
async def _startup() -> None:
    app.state.loop_task = asyncio.create_task(execution_loop())


@app.on_event("shutdown")
async def _shutdown() -> None:
    task = app.state.loop_task
    task.cancel()
    with suppress(asyncio.CancelledError):
        await task


def get_user_from_api_key(x_api_key: str = Header(default="")) -> User:
    user = db.get_user_by_key(x_api_key)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return user


@app.post("/user/create")
def create_user(body: CreateUserRequest) -> dict[str, str | int]:
    api_key = secrets.token_urlsafe(24)
    user = db.create_user(name=body.name, api_key=api_key)
    return {"id": user.id, "name": user.name, "api_key": user.api_key}


@app.post("/allocate")
def allocate(body: AllocationRequest, user: User = Depends(get_user_from_api_key)) -> dict[str, float]:
    db.set_allocation(user.id, body.capital)
    return {"capital": db.get_user_capital(user.id)}


@app.get("/dashboard")
def dashboard(user: User = Depends(get_user_from_api_key)) -> dict[str, float | int]:
    return db.user_dashboard(user.id)


@app.get("/my/trades")
def my_trades(user: User = Depends(get_user_from_api_key)) -> list[dict[str, str | float | int]]:
    return db.user_trades(user.id)


@app.get("/metrics/revenue")
def metrics_revenue() -> dict[str, float]:
    return {"platform_revenue": db.platform_revenue_total()}


@app.get("/metrics/live")
def metrics_live() -> dict[str, float | int]:
    return db.live_metrics()
