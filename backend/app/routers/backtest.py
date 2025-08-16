from fastapi import APIRouter
from ..schemas import BacktestIn, BacktestOut
from ..services.backtester import run_backtest

router = APIRouter()

@router.post("/backtest", response_model=BacktestOut)
def backtest(payload: BacktestIn):
    return run_backtest(payload)
