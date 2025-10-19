import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CHROMA_DB_PATH = "./chroma_db"

# ✅ Optimized for 8GB RAM
CHUNK_SIZE = 800        # Slightly larger chunks, fewer total
CHUNK_OVERLAP = 80      # Reduced overlap
SIMILARITY_THRESHOLD = 0.5  # Higher threshold for better quality
MAX_CHUNKS = 20         # Hard limit for 8GB systems