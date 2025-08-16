from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..deps import get_db, get_settings
from ..models import Symbol
from ..services.binance_client import refresh_symbols

router = APIRouter()

@router.get("/symbols")
def list_symbols(db: Session = Depends(get_db), settings=Depends(get_settings)):
    refreshed = refresh_symbols(db, settings.quote_asset)
    rows = db.query(Symbol).filter(
        Symbol.quote_asset == settings.quote_asset,
        Symbol.status == "TRADING"
    ).all()
    data = [dict(symbol=r.symbol, base_asset=r.base_asset, quote_asset=r.quote_asset,
                 tick_size=r.tick_size, step_size=r.step_size, min_notional=r.min_notional, status=r.status)
            for r in rows]
    return {"refreshed": refreshed, "count": len(data), "items": data}
