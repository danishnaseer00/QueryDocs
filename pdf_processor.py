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
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    def create_chunks(self, text: str) -> list[Document]:
        """Split text into chunks for vector storage."""
        documents = [Document(page_content=text)]
        chunks = self.text_splitter.split_documents(documents)
        return chunks