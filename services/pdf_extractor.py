import PyPDF2
from io import BytesIO

class PDFExtractor:
    @staticmethod
    def extract_text(pdf_content: bytes) -> str:
        try:
            pdf_file = BytesIO(pdf_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
        except Exception as e:
            raise Exception(f"Failed to extract PDF text: {str(e)}")

    @staticmethod
    def clean_text(text: str) -> str:
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.isspace():
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)