from sqlalchemy.orm import Session
from ..models import Position, Order, Trade, Signal
from datetime import datetime, timezone

def upsert_position(db: Session, symbol: str, qty: float, price: float, stop: float):
    pos = db.get(Position, symbol)
    now = datetime.now(timezone.utc)
    if not pos:
        pos = Position(symbol=symbol, qty=qty, avg_price=price, stop_price=stop)
        db.add(pos)
    else:
        total_qty = pos.qty + qty
        if total_qty <= 0:
            pos.qty = 0
            pos.avg_price = 0
            pos.stop_price = 0
        else:
            pos.avg_price = (pos.avg_price*pos.qty + price*qty) / total_qty
            pos.qty = total_qty
            pos.stop_price = stop
        pos.updated_at = now
    db.commit()
    return pos

def close_position(db: Session, symbol: str):
    pos = db.get(Position, symbol)
    if pos:
        db.delete(pos)
        db.commit()

def add_order_trade(db: Session, live: bool, symbol: str, side: str, qty: float, price: float, status: str="FILLED"):
    o = Order(live=live, symbol=symbol, side=side, qty=qty, price=price, status=status)
    db.add(o); db.commit(); db.refresh(o)
    t = Trade(order_id=o.id, symbol=symbol, qty=qty, price=price, fee=0.0)
    db.add(t); db.commit()
    return o, t

def add_signal(db: Session, symbol: str, timeframe: str, typ: str, reason: str, value: float):
    s = Signal(symbol=symbol, timeframe=timeframe, type=typ, reason=reason, value=value)
    db.add(s); db.commit()
