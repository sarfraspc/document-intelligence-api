"""
FastAPI application for the Document Intelligence System
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session
import os
import shutil

from app.db.database import engine, get_db
from app.db.models import Base, Document
from app.services.ocr_service import extract_text
from app.services.llm_service import answer_question  
from app.schemas import UploadResponse, AskRequest, AskResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Document Intelligence System",
    description="AI-powered image text extraction and question answering",
    version="0.1.0",
    lifespan=lifespan,
)


UPLOAD_DIR = "uploads"


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)):
    """
    Upload an image, extract text via OCR, and store in database.
    """
    # Basic validation
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file provided or filename missing",
        )

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type",
        )

    # Setup upload directory
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # Save file to disk with explicit cleanup
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save uploaded file: {str(e)}",
        )
    finally:
        file.file.close()  

    # Run OCR
    try:
        extracted_text = extract_text(file_path)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"OCR processing failed: {str(e)}",
        )

    # Persist to database
    try:
        document = Document(
            filename=file.filename,
            extracted_text=extracted_text,
        )
        db.add(document)
        db.commit()
        db.refresh(document)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save document to database: {str(e)}",
        )

    return UploadResponse(
        document_id=document.id,
        filename=document.filename,
    )


@app.post("/ask", response_model=AskResponse)
async def ask_question(
    payload: AskRequest,
    db: Session = Depends(get_db)):
    """
    Answer a natural language question about a previously uploaded document.
    """
    # Fetch document
    document = db.query(Document).filter(Document.id == payload.document_id).first()
    if not document:
        raise HTTPException(
            status_code=404,
            detail=f"Document with id {payload.document_id} not found",
        )

    # Check for extracted text
    if not document.extracted_text or document.extracted_text.strip() == "":
        raise HTTPException(
            status_code=400,
            detail="Document has no extracted text",
        )

    # LLM
    try:
        answer = answer_question(document.extracted_text, payload.question)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"LLM processing failed: {str(e)}",
        )

    return AskResponse(answer=answer)