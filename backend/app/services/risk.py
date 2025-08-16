def calc_stop(entry_price: float, atr: float, atr_mult: float) -> float:
    return max(0.0, entry_price - atr * atr_mult)
