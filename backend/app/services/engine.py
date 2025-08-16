"""
Worker de trading (APScheduler). 
- Paper: exécute via paper_broker
- Live: via live_broker
- Timeframe: settings.timeframe, on travaille par "candle close" en mode polling.
"""
from apscheduler.schedulers.blocking import BlockingScheduler
from sqlalchemy.orm import Session
from ..db import SessionLocal, init_db
from ..config import settings
from ..models import Symbol, Position
from .binance_client import refresh_symbols, klines
from .strategy import indicators, generate_signal
from .risk import calc_stop
from .state import add_signal, upsert_position, close_position, add_order_trade
from .paper_broker import market_buy as paper_buy, market_sell as paper_sell
from .live_broker import market_buy_live, market_sell_live

def _process_symbol(db: Session, symrow: Symbol):
    df = klines(symrow.symbol, interval=settings.timeframe, limit=200)
    df = indicators(df, settings.sma_fast, settings.sma_slow, settings.rsi_len, settings.atr_len)
    buy, exit_, last = generate_signal(df, settings.rsi_buy, settings.rsi_sell)

    last_close = float(last["close"])
    atr = float(last["atr"])
    # Position existante ?
    pos = db.get(Position, symrow.symbol)

    if settings.mode in ("paper","live"):
        if buy and (pos is None) :
            # sizing + minNotional check dans broker
            if settings.mode == "paper":
                res = paper_buy(db, symrow, last_close, settings.alloc_per_trade_eur)
                if res:
                    qty, price = res
                    stop = calc_stop(price, atr, settings.atr_mult_stop)
                    upsert_position(db, symrow.symbol, qty, price, stop)
                    add_signal(db, symrow.symbol, settings.timeframe, "BUY", "SMA20>50 & RSI>50", last_close)
            else:
                res = market_buy_live(db, symrow, last_close, settings.alloc_per_trade_eur)
                if res:
                    qty, price, _ = res
                    stop = calc_stop(price, atr, settings.atr_mult_stop)
                    upsert_position(db, symrow.symbol, qty, price, stop)
                    add_signal(db, symrow.symbol, settings.timeframe, "BUY", "SMA20>50 & RSI>50", last_close)

        if pos:
            # sortie par signal ou stop touché
            hit_stop = last_close <= pos.stop_price if pos.stop_price>0 else False
            if exit_ or hit_stop:
                qty = pos.qty
                if qty > 0:
                    if settings.mode == "paper":
                        res = paper_sell(db, symrow, last_close, qty)
                        if res:
                            qty_sold, price = res
                            close_position(db, symrow.symbol)
                            add_signal(db, symrow.symbol, settings.timeframe, "EXIT", "Trend off or stop", last_close)
                    else:
                        res = market_sell_live(db, symrow, last_close, qty)
                        if res:
                            qty_sold, price, _ = res
                            close_position(db, symrow.symbol)
                            add_signal(db, symrow.symbol, settings.timeframe, "EXIT", "Trend off or stop", last_close)

def job():
    db = SessionLocal()
    try:
        # Charger / rafraîchir univers
        refresh_symbols(db, settings.quote_asset)
        # respecter max positions
        active_positions = {p.symbol for p in db.query(Position).all()}
        # Tri des symboles (stables), filtre TRADING et présents dans settings.pairs
        wanted = [f"{b}{settings.quote_asset}" for b in settings.pairs]
        rows = db.query(Symbol).filter(Symbol.symbol.in_(wanted), Symbol.status=="TRADING").all()
        # Si déjà trop de positions, on traite d'abord celles ouvertes
        order = sorted(rows, key=lambda r: (r.symbol not in active_positions, r.symbol))
        for symrow in order:
            # respect max positions: on continue d'évaluer les pos existantes pour sorties,
            # mais on évite d'ouvrir de nouvelles au-delà de la limite
            before = len(active_positions)
            _process_symbol(db, symrow)
            # recompute active positions set
            active_positions = {p.symbol for p in db.query(Position).all()}
            if len(active_positions) >= settings.max_concurrent_pos:
                # On n’empêche pas les sorties; _process_symbol gère exits pour pos existantes
                pass
    finally:
        db.close()

def main():
    init_db()
    sched = BlockingScheduler(timezone="UTC")
    # Exé toutes les 60s: on travaille à la clôture de la bougie (clôture détectée via polling klines)
    sched.add_job(job, "interval", seconds=60, id="trading-loop", max_instances=1, coalesce=True)
    print("Worker started. Mode:", settings.mode, "Timeframe:", settings.timeframe)
    sched.start()

if __name__ == "__main__":
    main()
