# vector_store.py
import os
import shutil
import psutil
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.schema import Document
from config import FAISS_INDEX_PATH, SIMILARITY_THRESHOLD


class VectorStore:
    def __init__(self):
        print("Initializing embeddings model (CPU)...")
        self.embeddings = SentenceTransformerEmbeddings(
            model_name="sentence-transformers/paraphrase-MiniLM-L3-v2",
            model_kwargs={'device': 'cpu'}
        )
        self.vectorstore = None
        print("Embeddings model ready!")

    def create_vectorstore(self, chunks: list[Document]):
        """Create and save FAISS index from document chunks."""
        try:
            print(f"Creating FAISS vector store with {len(chunks)} chunks...")

            # Clear old index
            if os.path.exists(FAISS_INDEX_PATH):
                shutil.rmtree(FAISS_INDEX_PATH)
                print("Cleared old FAISS index.")

            # Dynamic chunk limiting based on RAM
            total_ram_gb = psutil.virtual_memory().total / (1024 ** 3)
            max_chunks = 10 if total_ram_gb <= 8 else 30
            if len(chunks) > max_chunks:
                print(f"Warning: Limiting to {max_chunks} chunks for low RAM.")
                chunks = chunks[:max_chunks]

            print("Building FAISS index...")
            self.vectorstore = FAISS.from_documents(
                documents=chunks,
                embedding=self.embeddings
            )

            print("Saving index to disk...")
            self.vectorstore.save_local(FAISS_INDEX_PATH)
            print("FAISS vector store created and saved!")

            return self.vectorstore

        except Exception as e:
            print(f"Error creating vector store: {e}")
            if os.path.exists(FAISS_INDEX_PATH):
                shutil.rmtree(FAISS_INDEX_PATH)
            raise

    def load_vectorstore(self):
        """Load FAISS index from disk."""
        try:
            if os.path.exists(FAISS_INDEX_PATH):
                print("Loading FAISS vector store...")
                self.vectorstore = FAISS.load_local(
                    folder_path=FAISS_INDEX_PATH,
                    embeddings=self.embeddings,
                    allow_dangerous_deserialization=True  # Required for local load
                )
                print("FAISS vector store loaded!")
                return self.vectorstore
            else:
                print("No FAISS index found.")
                return None
        except Exception as e:
            print(f"Error loading vector store: {e}")
            return None

    def similarity_search(self, query: str, k: int = 3):
        """Search for similar chunks with score."""
        if not self.vectorstore:
            self.load_vectorstore()
            if not self.vectorstore:
                return []

        try:
            print(f"Searching: {query[:50]}...")
            results = self.vectorstore.similarity_search_with_score(query, k=k)

            # Filter by similarity threshold (lower score = better)
            filtered = [(doc, score) for doc, score in results if score <= (1 - SIMILARITY_THRESHOLD)]
            print(f"Found {len(filtered)} relevant results.")
            return filtered

        except Exception as e:
            print(f"Search error: {e}")
            return []