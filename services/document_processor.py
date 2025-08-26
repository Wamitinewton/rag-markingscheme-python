import uuid
from typing import Dict, List
from services.pdf_extractor import PDFExtractor
from services.text_chunker import TextChunker
from services.embedding_service import EmbeddingService
from services.vector_store import VectorStore
from services.rag_service import RAGService
from services.pdf_generator import PDFGenerator

class DocumentProcessor:
    def __init__(self):
        self.pdf_extractor = PDFExtractor()
        self.text_chunker = TextChunker()
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()
        self.rag_service = RAGService()
        self.pdf_generator = PDFGenerator()
    
    def process_document(self, pdf_content: bytes, user_ip: str) -> Dict:
        document_id = str(uuid.uuid4())
        collection_name = f"collection_{user_ip.replace('.', '_')}"
        
        try:
            raw_text = self.pdf_extractor.extract_text(pdf_content)
            cleaned_text = self.pdf_extractor.clean_text(raw_text)
            
            chunks = self.text_chunker.chunk_text(cleaned_text)
            embeddings = self.embedding_service.create_embeddings(chunks)
            
            self.vector_store.create_collection(collection_name)
            self.vector_store.store_embeddings(collection_name, chunks, embeddings, document_id)
            
            questions = self.rag_service.extract_questions(cleaned_text)
            
            if not questions:
                raise Exception("No questions found in the document")
            
            questions_answers = self.rag_service.generate_answers(
                questions, cleaned_text, collection_name
            )
            
            pdf_path = self.pdf_generator.generate_answer_scheme(questions_answers, document_id)
            
            return {
                "message": "Document processed successfully",
                "document_id": document_id,
                "pdf_path": pdf_path,
                "questions_count": len(questions_answers)
            }
            
        except Exception as e:
            raise Exception(f"Document processing failed: {str(e)}")