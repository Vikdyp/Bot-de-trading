from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..deps import get_db
from ..services.portfolio import balances

router = APIRouter()

@router.get("/portfolio")
def portfolio(db: Session = Depends(get_db)):
    return balances(db)
