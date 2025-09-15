from sqlalchemy.orm import Session
from ..models import Position, Symbol
from .portfolio import get_or_init_portfolio
import math

def _round_step(value: float, step: float) -> float:
    if step <= 0:
        return value
    # floor au multiple de step (évite les rejections LOT_SIZE)
    return math.floor(value / step) * step

def market_buy(db: Session, sym: Symbol, price: float, alloc_eur: float):
    """
    Paper BUY en respectant LOT_SIZE et MIN_NOTIONAL.
    Débite le cash du portfolio.
    """
    # qty brute
    qty = alloc_eur / price
    # arrondi LOT_SIZE
    qty = _round_step(qty, sym.step_size)
    if qty <= 0:
        return None

    notional = qty * price
    if notional + 1e-9 < sym.min_notional:
        return None

    # vérif cash & débit
    port = get_or_init_portfolio(db)
    if port.cash_eur + 1e-9 < notional:
        return None
    port.cash_eur = max(0.0, port.cash_eur - notional)

    # upsert position (moyenne pondérée)
    pos = db.get(Position, sym.symbol)
    if not pos:
        pos = Position(symbol=sym.symbol, qty=qty, avg_price=price)
        db.add(pos)
    else:
        new_qty = pos.qty + qty
        pos.avg_price = (pos.avg_price * pos.qty + price * qty) / new_qty
        pos.qty = new_qty

    db.commit()
    return qty, price

def market_sell(db: Session, sym: Symbol, price: float, qty_req: float):
    """
    Paper SELL en respectant LOT_SIZE et MIN_NOTIONAL.
    Crédite le cash du portfolio.
    """
    pos = db.get(Position, sym.symbol)
    if not pos or pos.qty <= 0:
        return None

    # clamp à la qty dispo
    qty = min(qty_req, pos.qty)
    # arrondi LOT_SIZE
    qty = _round_step(qty, sym.step_size)
    if qty <= 0:
        return None

    notional = qty * price
    if notional + 1e-9 < sym.min_notional:
        return None

    # crédit cash
    port = get_or_init_portfolio(db)
    port.cash_eur = port.cash_eur + notional

    # maj position
    pos.qty -= qty
    if pos.qty <= 0:
        # on ferme la position (supprimer la ligne)
        db.delete(pos)

    db.commit()
    return qty, price
