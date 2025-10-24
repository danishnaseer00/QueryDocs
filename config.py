import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
FAISS_INDEX_PATH = "./faiss_index"

# ✅ OPTIMIZED FOR 8GB RAM + NO GPU
# Embedding model - smallest available
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # Only 80MB, was paraphrase-MiniLM-L3-v2

# Text chunking
CHUNK_SIZE = 300           # Reduced from 400
CHUNK_OVERLAP = 30         # Reduced from 50
MAX_CHUNKS = 12            # Reduced from 15
MAX_PAGES = 15             # Reduced from 20

# Vector search
SIMILARITY_THRESHOLD = 0.65  # Slightly relaxed from 0.6
TOP_K_RESULTS = 2           # Reduced from 3

# Memory limits
MAX_FILE_SIZE_MB = 8        # Reduced from 10MB
BATCH_SIZE = 5              # Process chunks in small batches

# LLM settings
LLM_TEMPERATURE = 0.2       # More deterministic
LLM_MAX_TOKENS = 512        # Limit response length