from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..deps import get_db
from ..models import Signal

router = APIRouter()

@router.get("/signals")
def list_signals(db: Session = Depends(get_db)):
    rows = db.query(Signal).order_by(Signal.id.desc()).limit(200).all()
    return [dict(symbol=r.symbol, timeframe=r.timeframe, type=r.type,
                 reason=r.reason, value=r.value, created_at=r.created_at.isoformat()) for r in rows]
