def sharpe(daily_returns, rf=0.0):
    import numpy as np
    if len(daily_returns) < 2: return 0.0
    return (np.mean(daily_returns) - rf) / (np.std(daily_returns) + 1e-9)
