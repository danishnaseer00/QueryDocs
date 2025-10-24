import os
import shutil
import gc
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.schema import Document
from config import (
    FAISS_INDEX_PATH, 
    SIMILARITY_THRESHOLD, 
    TOP_K_RESULTS,
    EMBEDDING_MODEL,
    BATCH_SIZE
)


class VectorStore:
    def __init__(self):
        """Initialize with smallest embedding model for low RAM."""
        print(f"Loading embedding model: {EMBEDDING_MODEL}")
        self.embeddings = SentenceTransformerEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={
                'device': 'cpu',
            },
            encode_kwargs={
                'batch_size': BATCH_SIZE,  # Process in small batches
            }
        )
        self.vectorstore = None
        print("✅ Embedding model loaded (CPU mode)")

    def create_vectorstore(self, chunks: list[Document]):
        """Create FAISS index with memory optimization."""
        try:
            print(f"Creating FAISS index with {len(chunks)} chunks...")

            # Clear old index
            if os.path.exists(FAISS_INDEX_PATH):
                shutil.rmtree(FAISS_INDEX_PATH)
                print("🗑️ Cleared old index")

            # Process in batches to avoid memory spikes
            print("📦 Processing chunks in batches...")
            all_vectorstores = []
            
            for i in range(0, len(chunks), BATCH_SIZE):
                batch = chunks[i:i + BATCH_SIZE]
                print(f"  Batch {i//BATCH_SIZE + 1}/{(len(chunks)-1)//BATCH_SIZE + 1}")
                
                batch_vs = FAISS.from_documents(
                    documents=batch,
                    embedding=self.embeddings
                )
                all_vectorstores.append(batch_vs)
                
                # Clear memory after each batch
                gc.collect()

            # Merge all batches
            print("🔗 Merging batches...")
            self.vectorstore = all_vectorstores[0]
            for vs in all_vectorstores[1:]:
                self.vectorstore.merge_from(vs)
            
            # Save to disk
            print("💾 Saving index...")
            os.makedirs(FAISS_INDEX_PATH, exist_ok=True)
            self.vectorstore.save_local(FAISS_INDEX_PATH)
            
            # Clear memory
            gc.collect()
            print("✅ FAISS index created successfully!")
            
            return self.vectorstore

        except Exception as e:
            print(f"❌ Error creating vector store: {e}")
            if os.path.exists(FAISS_INDEX_PATH):
                shutil.rmtree(FAISS_INDEX_PATH)
            raise

    def load_vectorstore(self):
        """Load FAISS index from disk."""
        try:
            if not os.path.exists(FAISS_INDEX_PATH):
                print("⚠️ No FAISS index found")
                return None
            
            print("📂 Loading FAISS index...")
            self.vectorstore = FAISS.load_local(
                folder_path=FAISS_INDEX_PATH,
                embeddings=self.embeddings,
                allow_dangerous_deserialization=True
            )
            print("✅ Index loaded!")
            return self.vectorstore
            
        except Exception as e:
            print(f"❌ Error loading index: {e}")
            return None

    def similarity_search(self, query: str, k: int = None):
        """Search with score filtering."""
        if k is None:
            k = TOP_K_RESULTS
            
        if not self.vectorstore:
            self.load_vectorstore()
            if not self.vectorstore:
                return []

        try:
            # Get results with scores
            results = self.vectorstore.similarity_search_with_score(query, k=k)
            
            # FAISS returns distance (lower is better)
            # Convert to similarity and filter
            filtered = []
            for doc, distance in results:
                # Convert distance to similarity (0-1 scale)
                similarity = 1 / (1 + distance)
                if similarity >= SIMILARITY_THRESHOLD:
                    filtered.append((doc, similarity))
            
            print(f"🔍 Found {len(filtered)}/{len(results)} relevant results")
            return filtered

        except Exception as e:
            print(f"❌ Search error: {e}")
            return []

    def get_retriever(self):
        """Get retriever for RAG chain."""
        if not self.vectorstore:
            self.load_vectorstore()
        
        if self.vectorstore:
            return self.vectorstore.as_retriever(
                search_kwargs={"k": TOP_K_RESULTS}
            )
        return None