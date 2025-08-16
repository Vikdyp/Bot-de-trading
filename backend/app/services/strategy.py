import pandas as pd
import ta

def indicators(df: pd.DataFrame, sma_fast: int, sma_slow: int, rsi_len: int, atr_len: int):
    out = df.copy()
    out["sma_fast"] = ta.trend.SMAIndicator(out["close"], window=sma_fast).sma_indicator()
    out["sma_slow"] = ta.trend.SMAIndicator(out["close"], window=sma_slow).sma_indicator()
    out["rsi"] = ta.momentum.RSIIndicator(out["close"], window=rsi_len).rsi()
    out["atr"] = ta.volatility.AverageTrueRange(out["high"], out["low"], out["close"], window=atr_len).average_true_range()
    return out

def generate_signal(df: pd.DataFrame, rsi_buy: float, rsi_sell: float):
    last = df.iloc[-1]
    prev = df.iloc[-2] if len(df) >= 2 else last
    buy = (last["sma_fast"] > last["sma_slow"]) and (prev["sma_fast"] <= prev["sma_slow"]) and (last["rsi"] > rsi_buy)
    exit_ = (last["sma_fast"] < last["sma_slow"]) or (last["rsi"] < rsi_sell)
    return buy, exit_, last
