import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CHROMA_DB_PATH = "./chroma_db"

# ✅ ULTRA-CONSERVATIVE SETTINGS FOR 8GB RAM
CHUNK_SIZE = 400        # Very small chunks
CHUNK_OVERLAP = 50      # Minimal overlap
SIMILARITY_THRESHOLD = 0.6  # Higher threshold = better quality
MAX_CHUNKS = 15         # Hard limit
MAX_PAGES = 20          # Max pages to process