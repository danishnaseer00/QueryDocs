import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from config import CHUNK_SIZE, CHUNK_OVERLAP, MAX_CHUNKS, MAX_PAGES

class PDFProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
        )
    
    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text with hard limits"""
        try:
            pdf_file.seek(0)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            if pdf_reader.is_encrypted:
                raise Exception("PDF is encrypted")
            
            num_pages = len(pdf_reader.pages)
            if num_pages > MAX_PAGES:
                raise Exception(f"PDF too large ({num_pages} pages). Max {MAX_PAGES} pages for 8GB RAM.")
            
            text = ""
            for i, page in enumerate(pdf_reader.pages):
                if i >= MAX_PAGES:  # Hard stop
                    break
                    
                page_text = page.extract_text()
                if page_text.strip():
                    text += page_text + "\n"
            
            if not text.strip():
                raise Exception("No text found in PDF")
                
            return text
            
        except Exception as e:
            raise Exception(f"PDF extraction error: {str(e)}")
    
    def create_chunks(self, text: str) -> list[Document]:
        """Create chunks with hard limit"""
        documents = [Document(page_content=text)]
        chunks = self.text_splitter.split_documents(documents)
        
        # ✅ Apply absolute limit
        if len(chunks) > MAX_CHUNKS:
            chunks = chunks[:MAX_CHUNKS]
            print(f"⚠️ Hard-limited to {MAX_CHUNKS} chunks")
            
        return chunks