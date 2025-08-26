import sys
import os
from pathlib import Path

current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse
from models.schemas import DocumentResponse, ProcessingStatus
from services.document_processor import DocumentProcessor

app = FastAPI(
    title="Past Paper Answer Generator",
    description="Upload past papers and generate answer schemes using RAG",
    version="1.0.0"
)

document_processor = DocumentProcessor()

@app.post("/upload-document", response_model=DocumentResponse)
async def upload_document(request: Request, file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    user_ip = request.client.host
    
    try:
        pdf_content = await file.read()
        
        if len(pdf_content) == 0:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        result = document_processor.process_document(pdf_content, user_ip)
        
        return DocumentResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{document_id}")
async def download_answer_scheme(document_id: str):
    from config.settings import settings
    
    if not os.path.exists(settings.OUTPUT_DIR):
        raise HTTPException(status_code=404, detail="Output directory not found")
    
    files = os.listdir(settings.OUTPUT_DIR)
    matching_files = [f for f in files if document_id in f]
    
    if not matching_files:
        raise HTTPException(status_code=404, detail="Answer scheme not found")
    
    file_path = os.path.join(settings.OUTPUT_DIR, matching_files[0])
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=f"answer_scheme_{document_id}.pdf",
        media_type='application/pdf'
    )

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

@app.get("/")
async def root():
    return {
        "message": "Past Paper Answer Generator API",
        "endpoints": {
            "upload": "/upload-document",
            "download": "/download/{document_id}",
            "health": "/health"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)