"""
Pydantic schemas for API requests/responses.
"""

from pydantic import BaseModel, ConfigDict

class UploadResponse(BaseModel):
    document_id: int
    filename: str

    model_config = ConfigDict(from_attributes=True)


class AskRequest(BaseModel):
    document_id: int
    question: str


class AskResponse(BaseModel):
    answer: str