from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..deps import get_db
from ..services.metrics import metrics as compute_metrics

router = APIRouter()

@router.get("/metrics")
def get_metrics(db: Session = Depends(get_db)):
    return compute_metrics(db)
