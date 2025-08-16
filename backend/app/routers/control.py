from fastapi import APIRouter
from ..config import settings

router = APIRouter()

@router.post("/paper/start")
def paper_start():
    settings.mode = "paper"
    return {"ok": True, "mode": settings.mode}

@router.post("/paper/stop")
def paper_stop():
    settings.mode = "stopped"
    return {"ok": True, "mode": settings.mode}

@router.post("/live/start")
def live_start():
    settings.mode = "live"
    return {"ok": True, "mode": settings.mode}

@router.post("/live/stop")
def live_stop():
    settings.mode = "stopped"
    return {"ok": True, "mode": settings.mode}
