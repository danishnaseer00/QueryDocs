import chromadb
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from config import CHROMA_DB_PATH
import os
import shutil

class VectorStore:
    def __init__(self):
        print("🔄 Initializing ultra-light embeddings...")
        # ✅ Use the absolute lightest model available
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        self.vectorstore = None

    def create_vectorstore(self, chunks: list[Document]):
        """Ultra-simple synchronous vector store creation"""
        try:
            print(f"🔄 Creating vector store with {len(chunks)} chunks...")
            
            # ✅ Always clean up existing DB first
            if os.path.exists(CHROMA_DB_PATH):
                shutil.rmtree(CHROMA_DB_PATH)
            
            # ✅ HARD LIMIT: Maximum 15 chunks for 8GB RAM
            if len(chunks) > 15:
                chunks = chunks[:15]
                print(f"⚠️ Limited to 15 chunks for 8GB RAM")
            
            print("⚙️ Building vector index...")
            
            # ✅ Direct synchronous creation - no fancy stuff
            self.vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory=CHROMA_DB_PATH
            )
            
            print("✅ Vector store created successfully!")
            return self.vectorstore
            
        except Exception as e:
            print(f"❌ Vector store error: {str(e)}")
            # Clean up on failure
            if os.path.exists(CHROMA_DB_PATH):
                shutil.rmtree(CHROMA_DB_PATH)
            raise

    def load_vectorstore(self):
        """Load existing vector store"""
        try:
            if os.path.exists(CHROMA_DB_PATH):
                self.vectorstore = Chroma(
                    persist_directory=CHROMA_DB_PATH,
                    embedding_function=self.embeddings
                )
                return self.vectorstore
            return None
        except Exception as e:
            print(f"❌ Load error: {e}")
            return None

    def similarity_search(self, query: str, k: int = 2):
        """Simple search"""
        if not self.vectorstore:
            self.load_vectorstore()
            
        if not self.vectorstore:
            return []
            
        try:
            results = self.vectorstore.similarity_search_with_score(query, k=k)
            return results
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []