from sqlalchemy.orm import Session
from .filters import enforce_filters
from ..models import Symbol
from .state import add_order_trade, upsert_position, close_position

def market_buy(db: Session, symrow: Symbol, last_price: float, alloc_eur: float):
    qty_raw = alloc_eur / last_price
    ok, price, qty, notion = enforce_filters(last_price, qty_raw, symrow.tick_size, symrow.step_size, symrow.min_notional)
    if not ok: 
        return None
    add_order_trade(db, live=False, symbol=symrow.symbol, side="BUY", qty=qty, price=price)
    # Stop placeholder défini ailleurs
    return qty, price

def market_sell(db: Session, symrow: Symbol, last_price: float, qty_to_sell: float):
    ok, price, qty, notion = enforce_filters(last_price, qty_to_sell, symrow.tick_size, symrow.step_size, symrow.min_notional)
    if not ok or qty <= 0: 
        return None
    add_order_trade(db, live=False, symbol=symrow.symbol, side="SELL", qty=qty, price=price)
    return qty, price
