import chromadb
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from config import CHROMA_DB_PATH, SIMILARITY_THRESHOLD
import shutil
import os

class VectorStore:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.vectorstore = None
        
    def create_vectorstore(self, chunks: list[Document], collection_name: str = "pdf_documents"):
        """Create a new vector store from document chunks."""
        # Clear existing database
        if os.path.exists(CHROMA_DB_PATH):
            shutil.rmtree(CHROMA_DB_PATH)
            
        self.vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=CHROMA_DB_PATH,
            collection_name=collection_name
        )
        self.vectorstore.persist()
        return self.vectorstore
    
    def load_vectorstore(self, collection_name: str = "pdf_documents"):
        """Load existing vector store."""
        if os.path.exists(CHROMA_DB_PATH):
            self.vectorstore = Chroma(
                persist_directory=CHROMA_DB_PATH,
                embedding_function=self.embeddings,
                collection_name=collection_name
            )
        return self.vectorstore
    
    def similarity_search(self, query: str, k: int = 3):
        """Search for similar documents."""
        if not self.vectorstore:
            return []
        
        results = self.vectorstore.similarity_search_with_score(query, k=k)
        # Filter results by similarity threshold
        filtered_results = [
            (doc, score) for doc, score in results 
            if score <= (1 - SIMILARITY_THRESHOLD)
        ]
        return filtered_results