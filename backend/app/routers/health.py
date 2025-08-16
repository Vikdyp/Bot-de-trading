from fastapi import APIRouter
from ..schemas import HealthOut

router = APIRouter()

@router.get("/health", response_model=HealthOut)
def health():
    return {"status":"ok", "version":"1.0.0"}
