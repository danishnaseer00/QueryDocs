
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CHROMA_DB_PATH = "./chroma_db"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
SIMILARITY_THRESHOLD = 0.7