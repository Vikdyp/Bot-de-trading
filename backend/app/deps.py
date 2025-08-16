from .db import SessionLocal
from .config import settings
from sqlalchemy.orm import Session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_settings():
    return settings
