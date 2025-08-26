from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib import colors
from typing import List, Dict
import os
from datetime import datetime
from config.settings import settings

class PDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        self.question_style = ParagraphStyle(
            'CustomQuestion',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=10,
            textColor=colors.darkred,
            leftIndent=20
        )
        
        self.answer_style = ParagraphStyle(
            'CustomAnswer',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=20,
            leftIndent=40,
            rightIndent=20
        )
    
    def generate_answer_scheme(self, questions_answers: List[Dict], document_id: str) -> str:
        os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"answer_scheme_{document_id}_{timestamp}.pdf"
        filepath = os.path.join(settings.OUTPUT_DIR, filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        story = []
        
        title = Paragraph("MARKING SCHEME", self.title_style)
        story.append(title)
        story.append(Spacer(1, 20))
        
        subtitle = Paragraph(f"Document ID: {document_id}", self.styles['Normal'])
        story.append(subtitle)
        story.append(Spacer(1, 30))
        
        for qa in questions_answers:
            question_text = f"{qa['question_number']}: {qa['question']}"
            question_para = Paragraph(question_text, self.question_style)
            story.append(question_para)
            
            answer_para = Paragraph(qa['answer'], self.answer_style)
            story.append(answer_para)
            story.append(Spacer(1, 15))
        
        try:
            doc.build(story)
            return filepath
        except Exception as e:
            raise Exception(f"Failed to generate PDF: {str(e)}")