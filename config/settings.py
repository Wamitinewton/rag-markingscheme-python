import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    QDRANT_URL = os.getenv("QDRANT_URL")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
    
    # Model configurations
    GPT_MODEL = "gpt-4-turbo-preview"
    EMBEDDING_MODEL = "text-embedding-3-large"
    
    # Chunking parameters
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    
    # Output directory
    OUTPUT_DIR = "generated_pdfs"

settings = Settings()