from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..deps import get_db
from ..models import Position

router = APIRouter()

@router.get("/positions")
def list_positions(db: Session = Depends(get_db)):
    rows = db.query(Position).all()
    return [
        {
            "symbol": r.symbol,
            "qty": r.qty,                 # 👈 ajouté
            "avg_price": r.avg_price,
            "stop_price": r.stop_price,
            "tp1_price": r.tp1_price,
            "tp1_done": r.tp1_done,
            "trail_active": r.trail_active,
            "trail_anchor": r.trail_anchor,
            "trail_dist": r.trail_dist,
            "opened_at": r.opened_at,
            "updated_at": r.updated_at,
        }
        for r in rows
    ]
