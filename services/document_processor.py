import uuid
from typing import Dict, List
from services.pdf_extractor import PDFExtractor
from services.answer_generator import AnswerGenerator

class DocumentProcessor:
    def __init__(self):
        self.pdf_extractor = PDFExtractor()
        self.answer_generator = AnswerGenerator()

    def process_document(self, pdf_content: bytes, user_ip: str) -> Dict:
        document_id = str(uuid.uuid4())
        try:
            raw_text = self.pdf_extractor.extract_text(pdf_content)
            cleaned_text = self.pdf_extractor.clean_text(raw_text)
            questions = self.answer_generator.extract_questions(cleaned_text)
            
            if not questions:
                raise Exception("No questions found in the document")
            
            questions_answers = self.answer_generator.generate_answers(questions, cleaned_text)
            
            return {
                "message": "Document processed successfully",
                "document_id": document_id,
                "questions_count": len(questions_answers),
                "questions_answers": questions_answers
            }
        except Exception as e:
            raise Exception(f"Document processing failed: {str(e)}")