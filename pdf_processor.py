import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from config import CHUNK_SIZE, CHUNK_OVERLAP

class PDFProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text from uploaded PDF file."""
        try:
            # Reset file pointer to beginning
            pdf_file.seek(0)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Check if PDF is encrypted
            if pdf_reader.is_encrypted:
                raise Exception("PDF is encrypted/password protected")
            
            # Check number of pages (limit for performance)
            num_pages = len(pdf_reader.pages)
            if num_pages > 100:
                raise Exception(f"PDF too large ({num_pages} pages). Maximum 100 pages allowed.")
            
            text = ""
            for i, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text.strip():  # Only add non-empty pages
                    text += page_text + "\n"
                
                # Show progress for large documents
                if i > 0 and i % 10 == 0:
                    print(f"Processed {i}/{num_pages} pages")
            
            if not text.strip():
                raise Exception("No text found in PDF. PDF might be image-based.")
                
            return text
            
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    def create_chunks(self, text: str) -> list[Document]:
        """Split text into chunks for vector storage."""
        documents = [Document(page_content=text)]
        chunks = self.text_splitter.split_documents(documents)
        return chunks