from ..schemas import BacktestIn, BacktestOut
from .binance_client import klines
from .strategy import indicators, generate_signal
from .risk import calc_stop

def backtest_pair(symbol: str, timeframe: str, params: dict):
    df = klines(symbol, interval=timeframe, limit=1000)
    df = indicators(df, params.get("sma_fast",20), params.get("sma_slow",50),
                       params.get("rsi_len",14), params.get("atr_len",14))
    cash = 1000.0
    pos_qty = 0.0
    pos_price = 0.0
    stop = 0.0
    trades = 0
    equity_curve = []
    for i in range(2, len(df)):
        sub = df.iloc[:i+1]
        buy, exit_, last = generate_signal(sub, params.get("rsi_buy",50), params.get("rsi_sell",45))
        price = float(last["close"])
        atr = float(last["atr"])
        if buy and pos_qty==0:
            pos_qty = cash/price
            pos_price = price
            stop = calc_stop(price, atr, params.get("atr_mult_stop",2.0))
            cash = 0.0
            trades += 1
        elif pos_qty>0 and (exit_ or price <= stop):
            cash = pos_qty * price
            pos_qty = 0.0
            pos_price = 0.0
            trades += 1
        # equity mark-to-market
        eq = cash + pos_qty*price
        equity_curve.append({"t": str(last["close_time"]), "equity": eq})
    # stats
    ret = equity_curve[-1]["equity"]/equity_curve[0]["equity"] - 1 if len(equity_curve)>1 else 0
    # drawdown
    peak = equity_curve[0]["equity"]
    dd = 0.0
    for p in equity_curve:
        if p["equity"] > peak: peak = p["equity"]
        dd = min(dd, p["equity"]/peak - 1.0)
    winrate = 0.5  # simplifié pour v1
    return ret, abs(dd), winrate, trades, equity_curve

def run_backtest(payload: BacktestIn) -> BacktestOut:
    params = payload.params
    total_ret = 0.0
    total_dd = 0.0
    total_trades = 0
    eq = []
    for base in payload.pairs:
        symbol = f"{base}{payload.timeframe and ''}"  # placeholder no-op (compat)
        symbol = f"{base}EUR"
        r, dd, wr, n, curve = backtest_pair(symbol, payload.timeframe, params)
        total_ret += r
        total_dd = max(total_dd, dd)
        total_trades += n
        if len(curve) > len(eq): eq = curve
    avg_ret = total_ret / max(1,len(payload.pairs))
    return BacktestOut(
        total_return=avg_ret,
        max_drawdown=total_dd,
        winrate=0.5,
        trades=total_trades,
        equity_curve=eq
    )
