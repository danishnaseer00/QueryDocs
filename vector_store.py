import chromadb
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.schema import Document
from config import CHROMA_DB_PATH, SIMILARITY_THRESHOLD
import shutil
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial

class VectorStore:
    def __init__(self):
        print("🔄 Initializing embeddings model...")
        self.embeddings = SentenceTransformerEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        self.vectorstore = None
        self.executor = ThreadPoolExecutor(max_workers=1)  # Single worker for CPU ops
        print("✅ Embeddings model initialized!")
    
    async def create_vectorstore_async(self, chunks: list[Document], collection_name: str = "pdf_documents"):
        """Create vector store asynchronously to avoid blocking."""
        try:
            print(f"🔄 Starting async vector store creation with {len(chunks)} chunks...")
            
            # Clear existing database
            if os.path.exists(CHROMA_DB_PATH):
                shutil.rmtree(CHROMA_DB_PATH)
                print("🗑️ Cleared existing database")
            
            # Limit chunks for stability (reduce further if needed)
            max_chunks = 20  # Reduced from 30
            if len(chunks) > max_chunks:
                print(f"⚠️ Limiting to first {max_chunks} chunks for stability")
                chunks = chunks[:max_chunks]
            
            print("🔍 Creating ChromaDB vector store in background...")
            
            # Run the blocking operation in a thread pool
            loop = asyncio.get_event_loop()
            create_func = partial(
                self._create_vectorstore_sync,
                chunks=chunks,
                collection_name=collection_name
            )
            
            # Set a timeout (adjust based on your needs)
            self.vectorstore = await asyncio.wait_for(
                loop.run_in_executor(self.executor, create_func),
                timeout=300  # 5 minutes timeout
            )
            
            print("✅ Vector store created successfully!")
            return self.vectorstore
            
        except asyncio.TimeoutError:
            print("❌ Vector store creation timed out")
            self._cleanup_failed_db()
            raise Exception("Vector store creation timed out. Try with fewer pages.")
        except Exception as e:
            print(f"❌ Error creating vector store: {str(e)}")
            self._cleanup_failed_db()
            raise Exception(f"Error creating vector store: {str(e)}")
    
    def _create_vectorstore_sync(self, chunks, collection_name):
        """Synchronous vector store creation (runs in thread)."""
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=CHROMA_DB_PATH,
            collection_name=collection_name
        )
        vectorstore.persist()
        return vectorstore
    
    def _cleanup_failed_db(self):
        """Clean up database on failure."""
        if os.path.exists(CHROMA_DB_PATH):
            try:
                shutil.rmtree(CHROMA_DB_PATH)
            except:
                pass
    
    # Synchronous fallback for non-async contexts
    def create_vectorstore(self, chunks: list[Document], collection_name: str = "pdf_documents"):
        """Synchronous wrapper - use create_vectorstore_async instead if possible."""
        print("⚠️ Using synchronous mode - may cause blocking")
        try:
            if os.path.exists(CHROMA_DB_PATH):
                shutil.rmtree(CHROMA_DB_PATH)
            
            # Even more aggressive limiting for sync mode
            if len(chunks) > 15:
                print(f"⚠️ Limiting to first 15 chunks in sync mode")
                chunks = chunks[:15]
            
            self.vectorstore = self._create_vectorstore_sync(chunks, collection_name)
            return self.vectorstore
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            self._cleanup_failed_db()
            raise
    
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
    
    async def similarity_search_async(self, query: str, k: int = 3):
        """Async search to avoid blocking."""
        if not self.vectorstore:
            self.load_vectorstore()
        
        if not self.vectorstore:
            return []
        
        try:
            print(f"🔍 Searching for: {query[:50]}...")
            
            # Run search in thread pool
            loop = asyncio.get_event_loop()
            search_func = partial(
                self.vectorstore.similarity_search_with_score,
                query=query,
                k=k
            )
            
            results = await asyncio.wait_for(
                loop.run_in_executor(self.executor, search_func),
                timeout=30  # 30 seconds timeout
            )
            
            # Filter results by similarity threshold
            filtered_results = [
                (doc, score) for doc, score in results 
                if score <= (1 - SIMILARITY_THRESHOLD)
            ]
            
            print(f"✅ Found {len(filtered_results)} relevant documents")
            return filtered_results
            
        except asyncio.TimeoutError:
            print("❌ Search timed out")
            return []
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []
    
    def similarity_search(self, query: str, k: int = 3):
        """Synchronous search - use similarity_search_async if possible."""
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
            
            print(f"✅ Found {len(filtered_results)} relevant documents")
            return filtered_results
            
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []
    
    def __del__(self):
        """Cleanup executor on deletion."""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)