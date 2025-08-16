from binance.client import Client
from sqlalchemy.orm import Session
from ..models import Symbol
from ..config import settings
import pandas as pd

def _client() -> Client:
    # Endpoints publics => clés non requises en paper
    key = settings.binance_key if settings.mode == "live" else None
    sec = settings.binance_secret if settings.mode == "live" else None
    return Client(api_key=key, api_secret=sec)

def _extract_filters(s: dict):
    tick = step = min_notional = None

    for f in s.get("filters", []):
        t = f.get("filterType")
        if t == "PRICE_FILTER":
            # tickSize obligatoire pour arrondir les prix
            tick = float(f.get("tickSize", "0"))
        elif t == "LOT_SIZE":
            # stepSize pour arrondir les quantités
            step = float(f.get("stepSize", "0"))
        # Ancien nom
        elif t == "MIN_NOTIONAL":
            v = f.get("minNotional")
            if v is not None:
                min_notional = float(v)
        # Nouveau nom (certaines paires ont migré)
        elif t == "NOTIONAL":
            # on prend minNotional si dispo, sinon minNotional en clé différente
            v = f.get("minNotional", f.get("minNotionalValue"))
            if v is not None:
                min_notional = float(v)

    return tick, step, min_notional

def refresh_symbols(db: Session, quote_asset: str):
    client = _client()
    info = client.get_exchange_info()
    symbols = info.get("symbols", [])

    count = 0
    for s in symbols:
        # Filtrer par quote (EUR) + statut
        if s.get("quoteAsset") != quote_asset:
            continue
        if s.get("status") != "TRADING":
            continue
        # Autorisé au SPOT ?
        if not s.get("isSpotTradingAllowed", True):
            continue
        perms = set(s.get("permissions", []))
        if perms and "SPOT" not in perms:
            continue

        tick, step, min_notional = _extract_filters(s)
        if not tick or not step or not min_notional:
            # On ignore si un filtre manque
            continue

        symbol_name = s.get("symbol")
        row = db.get(Symbol, symbol_name)
        if not row:
            row = Symbol(
                symbol=symbol_name,
                base_asset=s.get("baseAsset"),
                quote_asset=s.get("quoteAsset"),
                tick_size=tick,
                step_size=step,
                min_notional=min_notional,
                status=s.get("status"),
            )
            db.add(row)
        else:
            row.tick_size = tick
            row.step_size = step
            row.min_notional = min_notional
            row.status = s.get("status")
        count += 1

    db.commit()
    return count

def klines(symbol: str, interval: str = "1h", limit: int = 300):
    client = _client()
    raw = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    # [ open_time, open, high, low, close, volume, close_time, ... ]
    df = pd.DataFrame(raw, columns=[
        "open_time","open","high","low","close","volume","close_time","qav","trades","taker_base","taker_quote","ignore"
    ])
    for c in ["open","high","low","close","volume"]:
        df[c] = df[c].astype(float)
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    df["close_time"] = pd.to_datetime(df["close_time"], unit="ms", utc=True)
    return df[["open_time","high","low","close","volume","close_time"]]
