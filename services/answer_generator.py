from openai import OpenAI
from typing import List, Dict
import re
from config.settings import settings

class AnswerGenerator:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=30.0,
        )

    def extract_questions(self, text: str) -> List[Dict[str, str]]:
        questions = []
        
        main_q_pattern = (
            r"QUESTION\s+((?:\d+|ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|TEN))\s*\((\d+)\s*MARKS?\)\s*(.*?)"
            r"(?=QUESTION\s+(?:\d+|ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|TEN)|$)"
        )
        
        main_matches = re.findall(main_q_pattern, text, re.IGNORECASE | re.DOTALL)
        
        for question_num, marks, question_content in main_matches:

            sub_q_pattern = r"([a-z])\)\s*(.*?)(?=\s*[a-z]\)|$)"
            sub_matches = re.findall(sub_q_pattern, question_content, re.IGNORECASE | re.DOTALL)
            
            if sub_matches:
                for sub_letter, sub_content in sub_matches:
                    roman_pattern = r"(i{1,3}|iv|v|vi{0,3}|ix|x)\)\s*(.*?)(?=\s*(?:i{1,3}|iv|v|vi{0,3}|ix|x)\)|$)"
                    roman_matches = re.findall(roman_pattern, sub_content, re.IGNORECASE | re.DOTALL)
                    
                    if roman_matches:
                        for roman_num, roman_content in roman_matches:
                            clean_content = re.sub(r'\s+', ' ', roman_content.strip())
                            if len(clean_content) > 5:
                                questions.append({
                                    "number": f"{question_num}{sub_letter}{roman_num}",
                                    "content": clean_content,
                                    "marks": self._extract_marks_from_content(roman_content)
                                })
                    else:
                        clean_content = re.sub(r'\s+', ' ', sub_content.strip())
                        if len(clean_content) > 5:
                            questions.append({
                                "number": f"{question_num}{sub_letter}",
                                "content": clean_content,
                                "marks": self._extract_marks_from_content(sub_content)
                            })
            else:
                clean_content = re.sub(r'\s+', ' ', question_content.strip())
                if len(clean_content) > 5:
                    questions.append({
                        "number": question_num,
                        "content": clean_content,
                        "marks": marks
                    })
        
        return questions
    
    def _extract_marks_from_content(self, content: str) -> str:
        marks_pattern = r'\((\d+)\s*marks?\)'
        match = re.search(marks_pattern, content, re.IGNORECASE)
        return match.group(1) if match else "0"

    def generate_answers(self, questions: List[Dict[str, str]], document_context: str) -> List[Dict]:
        answers = []
        for i, question_data in enumerate(questions):
            try:
                prompt = self._create_answer_prompt(question_data, document_context)
                response = self.client.chat.completions.create(
                    model=settings.GPT_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=1500,
                    timeout=30.0,
                )
                answer = response.choices[0].message.content.strip()
                answers.append({
                    "question_number": question_data["number"],
                    "question": question_data["content"],
                    "answer": answer,
                    "marks": question_data["marks"]
                })
            except Exception as e:
                answers.append({
                    "question_number": question_data["number"],
                    "question": question_data["content"],
                    "answer": f"Error generating answer: {str(e)}",
                    "marks": question_data["marks"]
                })
        return answers

    def _create_answer_prompt(self, question_data: Dict[str, str], context: str) -> str:
        return f"""
You are an expert academic assistant providing concise answers for examination questions.

Document Content:
{context[:3000]}

Question: {question_data["content"]}
Marks: {question_data["marks"]}

Instructions:
1. Provide a focused, direct answer appropriate for the marks allocated
2. For questions worth 2-4 marks, give concise bullet points or brief explanations
3. For questions worth more marks, provide detailed explanations with examples
4. Base your answer on the document content when relevant, supplement with general knowledge
5. Keep answers well-structured and examination-appropriate
6. Format as plain text suitable for JSON

Answer:"""