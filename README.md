# Document Intelligence System

An AI-powered backend service that extracts text from document images (such as invoices or receipts) using OCR and answers natural-language questions using an open-source Large Language Model.

This project was implemented as part of the **Markovate – Junior AI/ML Engineer Coding Assignment**.

---

## 1. Architecture Overview

The system follows a clean, layered architecture with clear separation of concerns.

```
Client (Swagger / REST Client)
        |
        | HTTP (JSON / multipart)
        v
FastAPI Application
 ├── /upload   → Image upload + OCR
 ├── /ask      → Question answering using LLM
 └── /health   → Health check
        |
        v
Service Layer
 ├── OCR Service (Tesseract via pytesseract)
 └── LLM Service (FLAN-T5-small)
        |
        v
Persistence Layer
 └── SQLite database (SQLAlchemy ORM)
```

### Request Flow

1. User uploads an image using `/upload`
2. Image is saved locally and processed via OCR
3. Extracted text is stored in SQLite
4. User asks a question using `/ask`
5. The LLM generates an answer using the stored document text as context

---

## 2. Model & Library Choices (With Reasoning)

### OCR: Tesseract (via pytesseract)

- Explicitly allowed by the assignment
- Lightweight and CPU-friendly
- No large model downloads at runtime
- Suitable for structured documents like invoices and receipts
- Easier to run reliably inside Docker compared to heavier OCR frameworks

### LLM: google/flan-t5-small

- Open-source, instruction-tuned model
- Designed for question answering and reasoning tasks
- Small enough to run on CPU-only systems
- Deterministic generation (do_sample=False) ensures consistent responses
- Lower memory footprint compared to larger FLAN models

### Backend Framework: FastAPI

- High-performance async framework
- Automatic request validation using Pydantic
- Built-in OpenAPI/Swagger UI
- Clean dependency injection for database sessions

### Database: SQLite + SQLAlchemy

- Simple, file-based persistence
- Sufficient for multi-document storage
- SQLAlchemy ORM provides schema safety and clean abstractions

---

## 3. Completed Features

- Image upload with validation
- OCR-based text extraction
- LLM-based question answering (no rule-based logic)
- Persistent storage of documents and extracted text
- Support for multiple documents
- REST APIs with meaningful error handling
- Structured logging for reliability
- Unit and API tests using pytest
- Dockerized application with non-root execution
- Health check endpoint

---

## 4. Incomplete / Skipped Features

- Authentication and authorization
- Support for PDFs or multi-page documents
- Asynchronous background processing for OCR/LLM
- Chunking or retrieval strategies for very large documents
- Vector embeddings or semantic search
- Production-grade logging (structured logs, external log aggregation)
- Rate limiting and request throttling

---

## 5. Trade-offs & Engineering Decisions

- **CPU-only inference** was chosen to ensure portability and avoid GPU dependency
- **Tesseract OCR** was selected over heavier OCR libraries to reduce memory usage and improve Docker stability
- **SQLite** was used instead of PostgreSQL for simplicity and ease of setup
- **Single-pass prompt-based QA** was chosen over embeddings to keep the system simple and transparent
- **Model loaded at startup** improves request latency at the cost of slower cold start
- **OCR text is stored as raw text** rather than structured fields for flexibility

These trade-offs were made to prioritize reliability, clarity, and ease of deployment within limited time constraints.

---

## 6. Testing

Tests are written using **pytest** and include:

- API tests for `/upload`, `/ask`, and `/health`
- Validation of invalid inputs
- In-memory image generation for OCR testing
- End-to-end flow testing from upload to question answering

Run tests with:

```bash
pytest
```

---

## 7. Running the Application

### Local (without Docker)

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Docker

```bash
docker build -t document-intel .
docker run -p 8000:8000 document-intel
```

The API will be available at:

**http://localhost:8000**

Swagger UI:

**http://localhost:8000/docs**

---

## 8. API Endpoints

### `POST /upload`
Upload an image document and extract text via OCR

### `POST /ask`
Ask a natural-language question about a previously uploaded document

### `GET /health`
Health check endpoint

---

## 9. Improvements With More Time

- Add document chunking and context window management
- Introduce embeddings-based retrieval for long documents
- Support PDFs and multi-page inputs
- Improve OCR accuracy with preprocessing
- Add async task queues for OCR and LLM inference
- Use quantized or optimized LLM inference
- Add authentication, rate limiting, and monitoring

---

## Final Notes

This project focuses on **engineering fundamentals, clarity, and reliability** rather than feature completeness.