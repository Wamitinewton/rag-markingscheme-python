import sys
import os
from pathlib import Path

current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from models.schemas import DocumentResponse, ProcessingStatus
from services.document_processor import DocumentProcessor

app = FastAPI(
    title="Past Paper Answer Generator",
    description="Upload past papers and generate answer schemes",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "API is running",
        "version": "3.0.0"
    }

@app.get("/")
async def root():
    return {
        "message": "Past Paper Answer Generator API",
        "version": "3.0.0",
        "endpoints": {
            "upload": "/upload-document",
            "health": "/health",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=False
    )