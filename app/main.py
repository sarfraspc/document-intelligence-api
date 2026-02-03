"""
FastAPI application for the Document Intelligence System
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session
import os
import shutil
import logging

from app.db.database import engine, get_db
from app.db.models import Base, Document
from app.services.ocr_service import extract_text
from app.services.llm_service import answer_question  
from app.schemas import UploadResponse, AskRequest, AskResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application starting up - creating database tables")
    Base.metadata.create_all(bind=engine)
    yield
    logger.info("Application shutting down")


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
    logger.info(f"Upload request received: filename='{file.filename}', content_type='{file.content_type}'")
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
        logger.info(f"File saved to disk: {file_path}")
    except Exception as e:
        logger.error(f"Failed to save file {file.filename}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save uploaded file: {str(e)}",
        )
    finally:
        file.file.close()  

    # Run OCR
    try:
        logger.info(f"Starting OCR on {file_path}")
        extracted_text = extract_text(file_path)
        logger.info(f"OCR completed for {file.filename} - extracted {len(extracted_text)} characters")
    except Exception as e:
        logger.error(f"OCR failed for {file.filename}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"OCR processing failed: {str(e)}",
        )

    # Persist to database
    try:
        logger.info(f"Saving document metadata to database: filename='{file.filename}'")
        document = Document(
            filename=file.filename,
            extracted_text=extracted_text,
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        logger.info(f"Document saved successfully: id={document.id}")
    except Exception as e:
        logger.error(f"Database save failed for {file.filename}: {str(e)}")
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
    logger.info(f"Ask request: document_id={payload.document_id}, question='{payload.question}'")
    # Fetch document
    document = db.query(Document).filter(Document.id == payload.document_id).first()
    if not document:
        logger.warning(f"Document not found: id={payload.document_id}")
        raise HTTPException(
            status_code=404,
            detail=f"Document with id {payload.document_id} not found",
        )

    # Check for extracted text
    if not document.extracted_text or document.extracted_text.strip() == "":
        logger.warning(f"Empty extracted text for document id={payload.document_id}")
        raise HTTPException(
            status_code=400,
            detail="Document has no extracted text",
        )

    # LLM
    try:
        logger.info(f"Generating answer with LLM for document id={payload.document_id}")
        answer = answer_question(document.extracted_text, payload.question)
        logger.info(f"LLM answer generated (length={len(answer)})")
    except Exception as e:
        logger.error(f"LLM failed for document id={payload.document_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"LLM processing failed: {str(e)}",
        )

    return AskResponse(answer=answer)