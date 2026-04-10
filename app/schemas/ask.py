from pydantic import BaseModel, Field
from typing import List

class AskRequest(BaseModel):
    question: str = Field(..., min_length=5, max_length=500)

class Citation(BaseModel):
    source: str
    section: str
    text: str

class AskResponse(BaseModel):
    question: str
    answer: str
    citations: List[Citation]
    status: str
