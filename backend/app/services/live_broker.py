from binance.client import Client
from sqlalchemy.orm import Session
from ..config import settings
from ..models import Symbol
from .filters import enforce_filters

def _client():
    return Client(api_key=settings.binance_key, api_secret=settings.binance_secret)

def market_buy_live(db: Session, symrow: Symbol, last_price: float, alloc_eur: float):
    qty_raw = alloc_eur / last_price
    ok, price, qty, _ = enforce_filters(last_price, qty_raw, symrow.tick_size, symrow.step_size, symrow.min_notional)
    if not ok: return None
    c = _client()
    # Market order in QUANTITY
    order = c.create_order(symbol=symrow.symbol, side="BUY", type="MARKET", quantity=f"{qty:.8f}")
    return qty, price, order

def market_sell_live(db: Session, symrow: Symbol, last_price: float, qty_to_sell: float):
    ok, price, qty, _ = enforce_filters(last_price, qty_to_sell, symrow.tick_size, symrow.step_size, symrow.min_notional)
    if not ok or qty<=0: return None
    c = _client()
    order = c.create_order(symbol=symrow.symbol, side="SELL", type="MARKET", quantity=f"{qty:.8f}")
    return qty, price, order
