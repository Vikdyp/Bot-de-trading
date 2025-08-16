from fastapi import APIRouter
from ..config import settings

router = APIRouter()

@router.get("/portfolio")
def portfolio():
    # Minimal: retourne juste budget alloué et mode
    return {
        "mode": settings.mode,
        "budget_eur": settings.budget_eur,
        "alloc_per_trade_eur": settings.alloc_per_trade_eur,
        "max_concurrent_pos": settings.max_concurrent_pos
    }
