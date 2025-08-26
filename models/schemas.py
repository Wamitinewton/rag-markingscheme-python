from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class QuestionAnswer(BaseModel):
    question_number: str
    question: str
    answer: str
    marks: str

class DocumentResponse(BaseModel):
    message: str
    document_id: str
    questions_count: int
    questions_answers: List[QuestionAnswer]
    
    class Config:
        json_encoders = {
            str: str
        }