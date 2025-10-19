import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from config import CHUNK_SIZE, CHUNK_OVERLAP, MAX_CHUNKS

class PDFProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]  # Better separators
        )
    
    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text from uploaded PDF file."""
        try:
            pdf_file.seek(0)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            if pdf_reader.is_encrypted:
                raise Exception("PDF is encrypted/password protected")
            
            num_pages = len(pdf_reader.pages)
            # ✅ More conservative page limit for 8GB RAM
            if num_pages > 50:
                raise Exception(f"PDF too large ({num_pages} pages). Maximum 50 pages allowed for 8GB RAM systems.")
            
            text = ""
            for i, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text.strip():
                    text += page_text + "\n"
                
                # Early stopping for very large documents
                if i >= 30:  # Process max 30 pages for 8GB systems
                    print(f"⚠️ Processed first 30 pages (8GB RAM limit)")
                    break
            
            if not text.strip():
                raise Exception("No text found in PDF. PDF might be image-based.")
                
            return text
            
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    def create_chunks(self, text: str) -> list[Document]:
        """Split text into chunks with hard limit for 8GB RAM"""
        documents = [Document(page_content=text)]
        chunks = self.text_splitter.split_documents(documents)
        
        # ✅ Apply hard chunk limit for 8GB systems
        if len(chunks) > MAX_CHUNKS:
            print(f"⚠️ Limiting chunks from {len(chunks)} to {MAX_CHUNKS} for 8GB RAM")
            chunks = chunks[:MAX_CHUNKS]
            
        return chunks