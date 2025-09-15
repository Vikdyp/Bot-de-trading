from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from ..deps import get_db
from ..models import Symbol, Position
from ..services.paper_broker import market_buy as paper_buy, market_sell as paper_sell
from ..services.binance_client import klines
from ..config import settings

router = APIRouter()

class BuyBody(BaseModel):
    symbol: str = Field(..., description="ex: BTCEUR")
    alloc_eur: float = Field(..., gt=0)

class SellBody(BaseModel):
    symbol: str = Field(..., description="ex: BTCEUR")
    qty: float = Field(..., gt=0)

@router.post("/paper/buy")
def paper_buy_now(body: BuyBody, db: Session = Depends(get_db)):
    if settings.mode != "paper":
        raise HTTPException(400, "Only available in paper mode")
    sym = db.get(Symbol, body.symbol)
    if not sym:
        raise HTTPException(404, f"Symbol {body.symbol} not found; call /symbols first")
    # dernier close
    df = klines(body.symbol, interval=settings.timeframe, limit=1)
    if df.empty:
        raise HTTPException(400, "No price data")
    price = float(df["close"].iloc[-1])
    res = paper_buy(db, sym, price, body.alloc_eur)
    if not res:
        raise HTTPException(400, "Order rejected by filters or notional")
    qty, px = res
    return {"status":"ok", "symbol": body.symbol, "qty": qty, "price": px, "spent_eur": qty*px}

@router.post("/paper/sell")
def paper_sell_now(body: SellBody, db: Session = Depends(get_db)):
    if settings.mode != "paper":
        raise HTTPException(400, "Only available in paper mode")
    sym = db.get(Symbol, body.symbol)
    if not sym:
        raise HTTPException(404, f"Symbol {body.symbol} not found; call /symbols first")
    df = klines(body.symbol, interval=settings.timeframe, limit=1)
    if df.empty:
        raise HTTPException(400, "No price data")
    price = float(df["close"].iloc[-1])
    res = paper_sell(db, sym, price, body.qty)
    if not res:
        raise HTTPException(400, "Order rejected (qty too large/small?)")
    qty, px = res
    return {"status":"ok", "symbol": body.symbol, "qty": qty, "price": px, "received_eur": qty*px}

@router.post("/paper/close/{symbol}")
def paper_close_all(symbol: str, db: Session = Depends(get_db)):
    from ..models import Position, Symbol as Sym
    from ..services.paper_broker import market_sell
    from ..services.binance_client import klines
    from ..config import settings

    pos = db.get(Position, symbol)
    if not pos or pos.qty <= 0:
        return {"status": "noop", "detail": "No position"}

    sym = db.get(Sym, symbol)
    if not sym:
        return {"status": "error", "detail": f"Symbol {symbol} not found in DB (call /symbols)"}

    df = klines(symbol, interval=settings.timeframe, limit=1)
    if df.empty:
        return {"status": "error", "detail": "No price data"}

    price = float(df["close"].iloc[-1])
    res = market_sell(db, sym, price, pos.qty)
    if not res:
        return {"status": "error", "detail": "Sell rejected by filters"}
    qty, px = res
    return {"status": "ok", "symbol": symbol, "qty": qty, "price": px, "received_eur": qty*px}
