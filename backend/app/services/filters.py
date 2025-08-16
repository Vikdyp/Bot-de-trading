import math

def floor_to_step(x: float, step: float) -> float:
    if step == 0: return x
    return math.floor(x / step) * step

def round_to_tick(x: float, tick: float) -> float:
    if tick == 0: return x
    # Binance tolère arrondi au multiple de tick
    return math.floor(x / tick) * tick

def enforce_filters(price: float, qty: float, tick: float, step: float, min_notional: float):
    p = round_to_tick(price, tick)
    q = floor_to_step(qty, step)
    notional = p * q
    ok = notional >= min_notional and q > 0 and p > 0
    return ok, p, q, notional
