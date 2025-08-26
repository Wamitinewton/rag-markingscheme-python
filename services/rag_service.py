from openai import OpenAI
from typing import List, Dict
import json
import re
from config.settings import settings
from services.embedding_service import EmbeddingService
from services.vector_store import VectorStore

class RAGService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()
    
    def extract_questions(self, text: str) -> List[str]:
        question_patterns = [
            r'(?:^|\n)\s*(?:\d+\.?\s*(?:\([a-z]\))?\s*)(.*?\?)',
            r'(?:^|\n)\s*(?:Question\s+\d+:?\s*)(.*?\?)',
            r'(?:^|\n)\s*(?:[A-Z]\.\s*)(.*?\?)',
        ]
        
        questions = []
        for pattern in question_patterns:
            matches = re.findall(pattern, text, re.MULTILINE | re.IGNORECASE)
            questions.extend([match.strip() for match in matches if len(match.strip()) > 10])
        
        return list(set(questions))
    
    def generate_answers(self, questions: List[str], document_context: str, collection_name: str) -> List[Dict]:
        answers = []
        
        for i, question in enumerate(questions):
            try:
                query_embedding = self.embedding_service.create_embeddings([question])[0]
                relevant_chunks = self.vector_store.search_similar(
                    collection_name=collection_name,
                    query_embedding=query_embedding,
                    limit=3
                )
                
                context = "\n".join([chunk["text"] for chunk in relevant_chunks])
                
                prompt = self._create_answer_prompt(question, context)
                
                response = self.client.chat.completions.create(
                    model=settings.GPT_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=500
                )
                
                answer = response.choices[0].message.content.strip()
                
                answers.append({
                    "question_number": f"Q{i+1}",
                    "question": question,
                    "answer": answer
                })
                
            except Exception as e:
                answers.append({
                    "question_number": f"Q{i+1}",
                    "question": question,
                    "answer": f"Error generating answer: {str(e)}"
                })
        
        return answers
    
    def _create_answer_prompt(self, question: str, context: str) -> str:
        return f"""
You are an expert academic assistant tasked with providing comprehensive answers to examination questions.

Context from the document:
{context}

Question:
{question}

Instructions:
1. Provide a detailed, well-structured answer based on the given context
2. If the context doesn't contain sufficient information, use your knowledge to provide a reasonable answer
3. Structure your answer with clear explanations and examples where appropriate
4. Keep the answer focused and relevant to the question
5. Use bullet points or numbered lists only when necessary for clarity

Answer:"""