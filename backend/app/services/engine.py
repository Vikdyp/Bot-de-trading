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

def _apply_trailing(pos, last_close: float, atr: float):
    # met à jour trail selon config
    if not pos.trail_active:
        return pos.stop_price
    if settings.trail_mode.upper() == "ATR":
        dist = atr * settings.trail_value
    else:
        dist = last_close * float(settings.trail_value)
    # ancre = plus haut atteint
    anchor = max(pos.trail_anchor or last_close, last_close)
    pos.trail_anchor = anchor
    new_stop = anchor - dist
    return max(pos.stop_price, new_stop)

def _process_symbol(db: Session, symrow: Symbol):
    df = klines(symrow.symbol, interval=settings.timeframe, limit=200)
    df = indicators(df, settings.sma_fast, settings.sma_slow, settings.rsi_len, settings.atr_len)
    buy, exit_, last = generate_signal(df, settings.rsi_buy, settings.rsi_sell)

    last_close = float(last["close"])
    atr = float(last["atr"])
    sma_fast = float(last["sma_fast"])
    sma_slow = float(last["sma_slow"])
    rsi = float(last["rsi"])

    pos = db.get(Position, symrow.symbol)

    # --- Mise à jour trailing si position ouverte ----
    if pos:
        # TP1 ?
        if not pos.tp1_done and pos.tp1_price > 0 and last_close >= pos.tp1_price:
            # vendre TP1_PART en paper/live
            qty_tp = pos.qty * settings.tp1_part
            if settings.mode == "paper":
                res = paper_sell(db, symrow, last_close, qty_tp)
                if res:
                    qty_sold, price = res
                    pos.qty -= qty_sold
                    pos.avg_price = pos.avg_price  # inchangé
                    pos.tp1_done = True
                    # activer trailing sur le reste
                    pos.trail_active = True
                    db.commit()
            else:
                res = market_sell_live(db, symrow, last_close, qty_tp)
                if res:
                    qty_sold, price, _ = res
                    pos.qty -= qty_sold
                    pos.tp1_done = True
                    pos.trail_active = True
                    db.commit()

        # Trailing stop (met à jour stop_price)
        new_stop = _apply_trailing(pos, last_close, atr)
        if new_stop > (pos.stop_price or 0):
            pos.stop_price = new_stop
            db.commit()

        # sortie par signal ou stop touché
        hit_stop = last_close <= (pos.stop_price or 0)
        if exit_ or hit_stop:
            qty = pos.qty
            if qty > 0:
                if settings.mode == "paper":
                    res = paper_sell(db, symrow, last_close, qty)
                    if res:
                        close_position(db, symrow.symbol)
                        add_signal(db, symrow.symbol, settings.timeframe, "EXIT", "Trend off or stop", last_close)
                else:
                    res = market_sell_live(db, symrow, last_close, qty)
                    if res:
                        close_position(db, symrow.symbol)
                        add_signal(db, symrow.symbol, settings.timeframe, "EXIT", "Trend off or stop", last_close)
            return

    # --- Entrée (pas de position) ---
    if buy and pos is None:
        # lire balances
        from .portfolio import balances as read_bal
        bal = read_bal(db)
        nav = float(bal["nav"])
        cash = float(bal["cash_eur"])

        # force du signal
        from .sizing import signal_strength, dynamic_allocation_eur
        S = signal_strength(rsi, sma_fast, sma_slow)
        alloc = dynamic_allocation_eur(
            nav, cash, S,
            settings.max_alloc_pct,
            settings.risk_budget_eur,
            settings.min_alloc_eur
        )
        if alloc <= 0:
            return

        if settings.mode == "paper":
            res = paper_buy(db, symrow, last_close, alloc)
            if res:
                qty, price = res
                stop = calc_stop(price, atr, settings.atr_mult_stop)
                # TP1 & trailing init
                tp1 = price * (1.0 + settings.tp1_pct)
                trail_dist = atr * settings.trail_value if settings.trail_mode.upper()=="ATR" else price * float(settings.trail_value)
                # upsert
                p = upsert_position(db, symrow.symbol, qty, price, stop)
                p.tp1_price = tp1
                p.tp1_done = False
                p.trail_active = False  # activé après TP1 par défaut (ou mets True si tu veux trailing direct)
                p.trail_anchor = price
                p.trail_dist = trail_dist
                db.commit()
                add_signal(db, symrow.symbol, settings.timeframe, "BUY", f"S={S:.2f}", last_close)
                # décrémenter cash (paper)
                from .portfolio import get_or_init_portfolio
                port = get_or_init_portfolio(db)
                port.cash_eur = max(0.0, port.cash_eur - qty*price)
                db.commit()
        else:
            res = market_buy_live(db, symrow, last_close, alloc)
            if res:
                qty, price, _ = res
                stop = calc_stop(price, atr, settings.atr_mult_stop)
                p = upsert_position(db, symrow.symbol, qty, price, stop)
                p.tp1_price = price * (1.0 + settings.tp1_pct)
                p.tp1_done = False
                p.trail_active = False
                p.trail_anchor = price
                p.trail_dist = atr * settings.trail_value if settings.trail_mode.upper()=="ATR" else price * float(settings.trail_value)
                db.commit()
                add_signal(db, symrow.symbol, settings.timeframe, "BUY", f"S={S:.2f}", last_close)

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
