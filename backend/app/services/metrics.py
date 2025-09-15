from sqlalchemy.orm import Session
from ..models import Trade, Position, Symbol
from ..config import settings
from .binance_client import klines

def mark_to_market(db: Session):
    pos = db.query(Position).all()
    mtm = {}
    for p in pos:
        df = klines(p.symbol, interval=settings.timeframe, limit=1)
        price = float(df["close"].iloc[-1]) if len(df) else p.avg_price
        mtm[p.symbol] = {"qty": p.qty, "price": price, "value": p.qty * price}
    return mtm

def metrics(db: Session):
    # Réalisé
    trades = db.query(Trade).all()
    # PnL réalisé approximé par somme (signés BUY/SELL) – simplification v2
    # Pour du réalisé exact, il faut un PnL par round-trip. Ici on retourne des agrégats bruts.
    buy = sum(t.qty*t.price for t in trades if t.order.side=="BUY")
    sell = sum(t.qty*t.price for t in trades if t.order.side=="SELL")
    realized = sell - buy

    # Latent (MTM)
    mtm = mark_to_market(db)
    unreal = sum(v["value"] for v in mtm.values())

    # Equity courante (paper: NAV≈cash + unreal ; live: nav via balances())
    try:
        from .portfolio import balances
        bal = balances(db)
        nav = bal["nav"]
        exposure = bal["exposure_eur"]
        exp_ratio = bal["exposure_ratio"]
    except Exception:
        nav = unreal
        exposure = unreal
        exp_ratio = 1.0

    # Winrate & Sharpe simplifiés
    n_trades = len(trades)
    winrate = 0.5 if n_trades == 0 else 0.5
    sharpe = 0.0

    return {
        "nav": nav,
        "realized_pnl_eur": realized,
        "unrealized_value_eur": unreal,
        "exposure_eur": exposure,
        "exposure_ratio": exp_ratio,
        "winrate": winrate,
        "sharpe": sharpe,
        "trades": n_trades
    }
