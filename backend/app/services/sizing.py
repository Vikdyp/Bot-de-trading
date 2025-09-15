import math

def signal_strength(rsi: float, sma_fast: float, sma_slow: float):
    # RSI composante: map 50..80 -> 0..1 (bornage)
    s_rsi = max(0.0, min(1.0, (rsi - 50.0) / 30.0))
    # pente SMA: écart relatif
    if sma_slow > 0:
        s_trend = max(0.0, min(1.0, (sma_fast / sma_slow - 1.0) / 0.02))  # 2% d’écart -> 1
    else:
        s_trend = 0.0
    # combinaison
    return max(0.0, min(1.0, 0.6*s_rsi + 0.4*s_trend))

def dynamic_allocation_eur(nav: float, cash_eur: float, S: float, max_alloc_pct: float, risk_budget_eur: float, min_alloc_eur: float):
    cap_by_pct = nav * max_alloc_pct
    cap_by_signal = S * risk_budget_eur
    alloc = min(cash_eur, max(cap_by_signal, min_alloc_eur), cap_by_pct)
    return max(0.0, alloc)
