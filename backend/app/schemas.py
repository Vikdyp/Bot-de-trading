from pydantic import BaseModel, Field
from typing import List, Optional, Any

class HealthOut(BaseModel):
    status: str
    version: str

class ConfigOut(BaseModel):
    mode: str
    quote_asset: str
    timeframe: str
    pairs: List[str]
    budget_eur: float
    alloc_per_trade_eur: float
    max_concurrent_pos: int
    strategy: dict

class ConfigPatch(BaseModel):
    mode: Optional[str] = None
    timeframe: Optional[str] = None
    pairs: Optional[List[str]] = None
    alloc_per_trade_eur: Optional[float] = None
    max_concurrent_pos: Optional[int] = None
    strategy: Optional[dict] = None

class SymbolOut(BaseModel):
    symbol: str
    base_asset: str
    quote_asset: str
    tick_size: float
    step_size: float
    min_notional: float
    status: str

class SignalOut(BaseModel):
    symbol: str
    timeframe: str
    type: str
    reason: str
    value: float
    created_at: str

class OrderOut(BaseModel):
    id: int
    live: bool
    symbol: str
    side: str
    type: str
    qty: float
    price: float
    status: str
    created_at: str

class PositionOut(BaseModel):
    symbol: str
    qty: float
    avg_price: float
    stop_price: float
    opened_at: str
    updated_at: str

class BacktestIn(BaseModel):
    pairs: List[str]
    timeframe: str = "1h"
    start: str
    end: str
    params: dict = Field(default_factory=dict)

class BacktestOut(BaseModel):
    total_return: float
    max_drawdown: float
    winrate: float
    trades: int
    equity_curve: List[dict]
