import chromadb
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.schema import Document
from config import CHROMA_DB_PATH, SIMILARITY_THRESHOLD
import shutil
import os

class VectorStore:
    def __init__(self):
        print("🔄 Initializing embeddings model...")
        # Use the stable community embeddings
        self.embeddings = SentenceTransformerEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}  # Force CPU usage
        )
        self.vectorstore = None
        print("✅ Embeddings model initialized!")
        
    def create_vectorstore(self, chunks: list[Document], collection_name: str = "pdf_documents"):
        """Create a new vector store from document chunks."""
        try:
            print(f"🔄 Starting vector store creation with {len(chunks)} chunks...")
            
            # Clear existing database
            if os.path.exists(CHROMA_DB_PATH):
                shutil.rmtree(CHROMA_DB_PATH)
                print("🗑️ Cleared existing database")
            
            # Limit chunks for stability
            if len(chunks) > 30:
                print(f"⚠️ Limiting to first 30 chunks for stability")
                chunks = chunks[:30]
            
            print("🔍 Creating ChromaDB vector store (this may take a moment)...")
            
            # Create the vector store with all documents at once - simpler approach
            self.vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory=CHROMA_DB_PATH,
                collection_name=collection_name
            )
            
            print("💾 Persisting vector store...")
            self.vectorstore.persist()
            
            print("✅ Vector store created successfully!")
            return self.vectorstore
            
        except Exception as e:
            print(f"❌ Error creating vector store: {str(e)}")
            # Clean up on failure
            if os.path.exists(CHROMA_DB_PATH):
                try:
                    shutil.rmtree(CHROMA_DB_PATH)
                except:
                    pass
            raise Exception(f"Error creating vector store: {str(e)}")
    
    def load_vectorstore(self, collection_name: str = "pdf_documents"):
        """Load existing vector store."""
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
            print(f"❌ Error loading vector store: {str(e)}")
            return None
    
    def similarity_search(self, query: str, k: int = 3):
        """Search for similar documents."""
        if not self.vectorstore:
            self.load_vectorstore()
            
        if not self.vectorstore:
            return []
        
        try:
            print(f"🔍 Searching for: {query[:50]}...")
            results = self.vectorstore.similarity_search_with_score(query, k=k)
            
            # Filter results by similarity threshold
            filtered_results = [
                (doc, score) for doc, score in results 
                if score <= (1 - SIMILARITY_THRESHOLD)
            ]
            
            print(f"✅ Found {len(filtered_results)} relevant documents")
            return filtered_results
            
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []