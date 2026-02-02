"""
Database configuration.
Uses SQLite
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_URL = "sqlite:///./documents.db"

engine = create_engine(
    SQLALCHEMY_URL,
    connect_args={"check_same_thread": False} 
)

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()