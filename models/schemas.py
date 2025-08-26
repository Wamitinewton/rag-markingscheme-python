from pydantic import BaseModel
from typing import List, Dict, Any

class QuestionAnswer(BaseModel):
    question: str
    answer: str
    question_number: str

class DocumentResponse(BaseModel):
    message: str
    document_id: str
    pdf_path: str
    questions_count: int

class ProcessingStatus(BaseModel):
    status: str
    message: str
    document_id: str = None