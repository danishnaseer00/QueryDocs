
import chromadb
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.schema import Document
from config import CHROMA_DB_PATH, SIMILARITY_THRESHOLD
import shutil
import os
import asyncio
from concurrent.futures import ProcessPoolExecutor
from functools import partial
import psutil


class VectorStore:
    def __init__(self):
        print("🔄 Initializing embeddings model (CPU-optimized)...")
        # ✅ Smaller model for low-RAM CPU
        self.embeddings = SentenceTransformerEmbeddings(
            model_name="sentence-transformers/paraphrase-MiniLM-L3-v2",
            model_kwargs={'device': 'cpu'}
        )
        self.vectorstore = None

        # ✅ Use process pool for CPU tasks (avoids GIL)
        self.executor = ProcessPoolExecutor(max_workers=2)
        print("✅ Embeddings model initialized successfully!")

    async def create_vectorstore_async(self, chunks: list[Document], collection_name: str = "pdf_documents"):
        """Create Chroma vector store asynchronously (CPU safe)."""
        try:
            print(f"🔄 Starting vector store creation with {len(chunks)} chunks...")

            # ✅ Only remove DB if it’s corrupt or not existing
            if not os.path.exists(CHROMA_DB_PATH):
                os.makedirs(CHROMA_DB_PATH, exist_ok=True)
            else:
                print("📁 Existing DB found — skipping full wipe.")

            # ✅ Dynamic limit based on available RAM
            total_ram = psutil.virtual_memory().total / (1024 ** 3)
            if total_ram <= 8:
                max_chunks = 10
            else:
                max_chunks = 30

            if len(chunks) > max_chunks:
                print(f"⚠️ Limiting chunks to {max_chunks} to prevent memory crash.")
                chunks = chunks[:max_chunks]

            loop = asyncio.get_event_loop()
            create_func = partial(self._create_vectorstore_sync, chunks, collection_name)

            # ✅ Run in separate process (no blocking)
            self.vectorstore = await asyncio.wait_for(
                loop.run_in_executor(self.executor, create_func),
                timeout=300  # 5 min timeout
            )

            print("✅ Vector store created and persisted successfully!")
            return self.vectorstore

        except asyncio.TimeoutError:
            print("❌ Vector store creation timed out.")
            raise Exception("Vector store creation took too long. Try fewer pages.")
        except Exception as e:
            print(f"❌ Error creating vector store: {str(e)}")
            raise

    def _create_vectorstore_sync(self, chunks, collection_name):
        """Runs in separate process (safe for CPU-bound ops)."""
        print("⚙️ Building Chroma index on CPU...")
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=CHROMA_DB_PATH,
            collection_name=collection_name
        )
        vectorstore.persist()
        return vectorstore

    def load_vectorstore(self, collection_name: str = "pdf_documents"):
        """Load an existing persisted vector store."""
        try:
            if os.path.exists(CHROMA_DB_PATH):
                print("🔄 Loading existing Chroma vector store...")
                self.vectorstore = Chroma(
                    persist_directory=CHROMA_DB_PATH,
                    embedding_function=self.embeddings,
                    collection_name=collection_name
                )
                print("✅ Vector store loaded successfully!")
                return self.vectorstore
            else:
                print("⚠️ No existing database found.")
                return None
        except Exception as e:
            print(f"❌ Error loading vector store: {e}")
            return None

    async def similarity_search_async(self, query: str, k: int = 3):
        """Perform similarity search asynchronously."""
        if not self.vectorstore:
            self.load_vectorstore()

        if not self.vectorstore:
            return []

        try:
            print(f"🔍 Performing search for: {query[:50]}...")

            loop = asyncio.get_event_loop()
            search_func = partial(
                self.vectorstore.similarity_search_with_score,
                query=query,
                k=k
            )

            results = await asyncio.wait_for(
                loop.run_in_executor(self.executor, search_func),
                timeout=30
            )

            filtered_results = [
                (doc, score) for doc, score in results
                if score <= (1 - SIMILARITY_THRESHOLD)
            ]

            print(f"✅ Found {len(filtered_results)} relevant documents.")
            return filtered_results

        except asyncio.TimeoutError:
            print("❌ Search timed out.")
            return []
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []

    def similarity_search(self, query: str, k: int = 3):
        """Synchronous fallback for quick testing."""
        if not self.vectorstore:
            self.load_vectorstore()

        if not self.vectorstore:
            return []

        try:
            print(f"🔍 Searching for: {query[:50]}...")
            results = self.vectorstore.similarity_search_with_score(query, k=k)

            filtered_results = [
                (doc, score) for doc, score in results
                if score <= (1 - SIMILARITY_THRESHOLD)
            ]

            print(f"✅ Found {len(filtered_results)} relevant documents.")
            return filtered_results

        except Exception as e:
            print(f"❌ Search error: {e}")
            return []

    def __del__(self):
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)
