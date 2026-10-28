import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_KEY")
TEXTBOOKS_DIR = "Textbooks"
VECTOR_DB_DIR = "vector_db_gemini_rebuild_1"
EMBEDDING_MODEL = "gemini-embedding-001"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
NUM_RETRIEVED_DOCS = 5  # More docs for better context
TEMPERATURE = 0.3  # Slightly higher for educational explanations

MODEL_NAME = "gemini-3.8-flash" 
