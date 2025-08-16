from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..deps import get_db
from ..models import Position

router = APIRouter()

@router.get("/positions")
def list_positions(db: Session = Depends(get_db)):
    rows = db.query(Position).all()
    return [dict(symbol=r.symbol, qty=r.qty, avg_price=r.avg_price, stop_price=r.stop_price,
                 opened_at=r.opened_at.isoformat(), updated_at=r.updated_at.isoformat()) for r in rows]
