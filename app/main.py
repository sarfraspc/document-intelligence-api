"""
FastAPI application for the Document Intelligence System
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.db.database import engine
from app.db.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # tables
    Base.metadata.create_all(bind=engine)
    yield



app = FastAPI(
    title="Document Intelligence System",
    description="AI-powered document text extraction and question answering",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}