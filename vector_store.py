import chromadb
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.schema import Document
from config import CHROMA_DB_PATH, SIMILARITY_THRESHOLD
import os
import psutil

class VectorStore:
    def __init__(self):
        print("🔄 Initializing lightweight embeddings model...")
        # ✅ Use ultra-light model for 8GB RAM
        self.embeddings = SentenceTransformerEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",  # Much smaller and faster
            model_kwargs={'device': 'cpu'}
        )
        self.vectorstore = None
        print("✅ Lightweight embeddings model initialized!")

    def create_vectorstore(self, chunks: list[Document], collection_name: str = "pdf_documents"):
        """Create Chroma vector store synchronously - much faster"""
        try:
            print(f"🔄 Creating vector store with {len(chunks)} chunks...")
            
            # ✅ Clear existing DB to avoid conflicts
            if os.path.exists(CHROMA_DB_PATH):
                import shutil
                shutil.rmtree(CHROMA_DB_PATH)
            
            # ✅ Limit chunks based on available RAM
            total_ram = psutil.virtual_memory().total / (1024 ** 3)
            if total_ram <= 8:
                max_chunks = min(20, len(chunks))  # Very conservative for 8GB RAM
                if len(chunks) > max_chunks:
                    print(f"⚠️ Limiting to {max_chunks} chunks for 8GB RAM system")
                    chunks = chunks[:max_chunks]
            
            # ✅ Direct synchronous creation - much faster
            print("⚙️ Building Chroma index...")
            self.vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory=CHROMA_DB_PATH,
                collection_name=collection_name
            )
            
            print("✅ Vector store created successfully!")
            return self.vectorstore

        except Exception as e:
            print(f"❌ Error creating vector store: {str(e)}")
            # Clean up on error
            if os.path.exists(CHROMA_DB_PATH):
                import shutil
                shutil.rmtree(CHROMA_DB_PATH)
            raise

    def load_vectorstore(self, collection_name: str = "pdf_documents"):
        """Load existing vector store"""
        try:
            if os.path.exists(CHROMA_DB_PATH):
                print("🔄 Loading existing vector store...")
                self.vectorstore = Chroma(
                    persist_directory=CHROMA_DB_PATH,
                    embedding_function=self.embeddings,
                    collection_name=collection_name
                )
                print("✅ Vector store loaded!")
                return self.vectorstore
            return None
        except Exception as e:
            print(f"❌ Error loading vector store: {e}")
            return None

    def similarity_search(self, query: str, k: int = 2):  # Reduced from 3 to 2
        """Fast synchronous similarity search"""
        if not self.vectorstore:
            self.load_vectorstore()

        if not self.vectorstore:
            return []

        try:
            results = self.vectorstore.similarity_search_with_score(query, k=k)
            
            # Filter by similarity threshold
            filtered_results = [
                (doc, score) for doc, score in results
                if score <= (1 - SIMILARITY_THRESHOLD)
            ]
            
            return filtered_results

        except Exception as e:
            print(f"❌ Search error: {e}")
            return []