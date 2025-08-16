from fastapi import APIRouter, Depends
from ..deps import get_settings
from ..schemas import ConfigOut, ConfigPatch
from ..config import settings as _settings

router = APIRouter()

@router.get("/config", response_model=ConfigOut)
def get_config(settings = Depends(get_settings)):
    return {
        "mode": settings.mode,
        "quote_asset": settings.quote_asset,
        "timeframe": settings.timeframe,
        "pairs": settings.pairs,
        "budget_eur": settings.budget_eur,
        "alloc_per_trade_eur": settings.alloc_per_trade_eur,
        "max_concurrent_pos": settings.max_concurrent_pos,
        "strategy": {
            "sma_fast": settings.sma_fast,
            "sma_slow": settings.sma_slow,
            "rsi_len": settings.rsi_len,
            "rsi_buy": settings.rsi_buy,
            "rsi_sell": settings.rsi_sell,
            "atr_len": settings.atr_len,
            "atr_mult_stop": settings.atr_mult_stop,
        }
    }

@router.patch("/config", response_model=ConfigOut)
def patch_config(payload: ConfigPatch):
    # Simple in-memory patch for demo; en prod on persisterait en DB
    if payload.mode: _settings.mode = payload.mode
    if payload.timeframe: _settings.timeframe = payload.timeframe
    if payload.pairs: _settings.pairs = payload.pairs
    if payload.alloc_per_trade_eur is not None: _settings.alloc_per_trade_eur = payload.alloc_per_trade_eur
    if payload.max_concurrent_pos is not None: _settings.max_concurrent_pos = payload.max_concurrent_pos
    if payload.strategy:
        for k,v in payload.strategy.items():
            if hasattr(_settings, k): setattr(_settings, k, v)
    return get_config(_settings)
