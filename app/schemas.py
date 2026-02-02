"""
Pydantic schemas for API requests/responses
"""

from pydantic import BaseModel


class UploadResponse(BaseModel):
    document_id: int
    filename: str

    class Config:
        from_attributes = True 