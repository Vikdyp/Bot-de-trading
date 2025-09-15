from sqlalchemy.orm import Session
from .binance_client import _client
from ..config import settings
from ..models import Portfolio, Position, Symbol
from .binance_client import klines
import math

def get_or_init_portfolio(db: Session) -> Portfolio:
    row = db.query(Portfolio).first()
    if not row:
        row = Portfolio(cash_eur=settings.paper_cash_eur)
        db.add(row); db.commit()
    return row

def get_prices_map(client) -> dict:
    tickers = client.get_ticker()  # 24h tickers
    # map "SYMBOL" -> lastPrice
    return {t["symbol"]: float(t["lastPrice"]) for t in tickers}

def live_balances(db: Session):
    client = _client()
    prices = get_prices_map(client)
    acc = client.get_account()
    balances = acc["balances"]
    # EUR cash
    eur_bal = next((b for b in balances if b["asset"]=="EUR"), {"free":"0","locked":"0"})
    eur_free = float(eur_bal["free"])
    # positions valorisées
    pos_rows = db.query(Position).all()
    nav = eur_free
    exposure = 0.0
    details = {"EUR": eur_free}
    for p in pos_rows:
        price = prices.get(p.symbol, 0.0)
        val = p.qty * price
        details[p.symbol] = val
        nav += val
        exposure += val
    exp_ratio = exposure / max(1e-9, nav)
    return {"mode":"live", "nav": nav, "cash_eur": eur_free, "exposure_eur": exposure, "exposure_ratio": exp_ratio, "breakdown": details}

def paper_balances(db: Session):
    port = get_or_init_portfolio(db)
    # valoriser positions avec dernières closes
    pos_rows = db.query(Position).all()
    exposure = 0.0
    details = {"EUR": port.cash_eur}
    nav = port.cash_eur
    # simplifié: dernier kline close
    from ..models import Symbol
    for p in pos_rows:
        sym = db.get(Symbol, p.symbol)
        # on peut utiliser le dernier close via klines(limit=1)
        df = klines(p.symbol, interval=settings.timeframe, limit=1)
        price = float(df["close"].iloc[-1]) if len(df) else p.avg_price
        val = p.qty * price
        nav += val
        exposure += val
        details[p.symbol] = val
    exp_ratio = exposure / max(1e-9, nav)
    return {"mode":"paper", "nav": nav, "cash_eur": port.cash_eur, "exposure_eur": exposure, "exposure_ratio": exp_ratio, "breakdown": details}

def balances(db: Session):
    return live_balances(db) if settings.mode=="live" else paper_balances(db)
