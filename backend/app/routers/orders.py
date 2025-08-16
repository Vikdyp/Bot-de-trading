from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..deps import get_db
from ..models import Order, Trade

router = APIRouter()

@router.get("/orders")
def list_orders(db: Session = Depends(get_db)):
    rows = db.query(Order).order_by(Order.id.desc()).limit(200).all()
    return [dict(id=r.id, live=r.live, symbol=r.symbol, side=r.side, type=r.type,
                 qty=r.qty, price=r.price, status=r.status, created_at=r.created_at.isoformat()) for r in rows]

@router.get("/trades")
def list_trades(db: Session = Depends(get_db)):
    rows = db.query(Trade).order_by(Trade.id.desc()).limit(200).all()
    return [dict(id=r.id, order_id=r.order_id, symbol=r.symbol, qty=r.qty, price=r.price,
                 fee=r.fee, created_at=r.created_at.isoformat()) for r in rows]
