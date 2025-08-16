from fastapi import FastAPI
from .db import init_db
from .routers import health, config, symbols, control, portfolio, positions, orders, signals, backtest

init_db()
app = FastAPI(title="Binance EUR Bot", version="1.0.0")

# ❌ Ne PAS mettre prefix="/"
app.include_router(health.router, tags=["health"])
app.include_router(config.router, tags=["config"])
app.include_router(symbols.router, tags=["symbols"])
app.include_router(control.router, tags=["control"])
app.include_router(portfolio.router, tags=["portfolio"])
app.include_router(positions.router, tags=["positions"])
app.include_router(orders.router, tags=["orders"])
app.include_router(signals.router, tags=["signals"])
app.include_router(backtest.router, tags=["backtest"])
