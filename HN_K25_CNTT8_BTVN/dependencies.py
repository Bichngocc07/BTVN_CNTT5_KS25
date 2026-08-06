from typing import Generator
from sqlalchemy.orm import Session
from database import SessionLocal

def get_db() -> Generator[Session, None, None]:
    """Dependency cung cấp Session CSDL và tự động đóng kết nối khi hoàn tất."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()