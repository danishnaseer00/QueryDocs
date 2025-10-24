import PyPDF2
import gc
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from config import (
    CHUNK_SIZE, 
    CHUNK_OVERLAP, 
    MAX_CHUNKS, 
    MAX_PAGES,
    MAX_FILE_SIZE_MB
)


class PDFProcessor:
    def __init__(self):
        """Initialize text splitter with optimal settings."""
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]  # Better splitting
        )
    
    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text with strict memory limits."""
        try:
            # Check file size
            pdf_file.seek(0, 2)  # Seek to end
            file_size_bytes = pdf_file.tell()
            pdf_file.seek(0)  # Reset to start
            
            file_size_mb = file_size_bytes / (1024 * 1024)
            
            if file_size_mb > MAX_FILE_SIZE_MB:
                raise Exception(
                    f"File too large: {file_size_mb:.1f}MB. "
                    f"Maximum: {MAX_FILE_SIZE_MB}MB for your system."
                )
            
            print(f"📄 Processing PDF ({file_size_mb:.1f}MB)...")
            
            # Read PDF
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Check encryption
            if pdf_reader.is_encrypted:
                raise Exception("PDF is password-protected")
            
            # Check page count
            num_pages = len(pdf_reader.pages)
            print(f"📖 Total pages: {num_pages}")
            
            if num_pages > MAX_PAGES:
                print(f"⚠️ Limiting to first {MAX_PAGES} pages")
                num_pages = MAX_PAGES
            
            # Extract text page by page
            text_parts = []
            for i in range(num_pages):
                try:
                    page = pdf_reader.pages[i]
                    page_text = page.extract_text()
                    
                    if page_text and page_text.strip():
                        text_parts.append(page_text)
                        
                        # Progress indicator
                        if (i + 1) % 5 == 0:
                            print(f"  Processed {i + 1}/{num_pages} pages")
                    
                except Exception as e:
                    print(f"  ⚠️ Skipping page {i + 1}: {e}")
                    continue
            
            # Combine text
            full_text = "\n\n".join(text_parts)
            
            # Clear memory
            del pdf_reader, text_parts
            gc.collect()
            
            # Validate extracted text
            if len(full_text.strip()) < 100:
                raise Exception(
                    "PDF contains very little text. "
                    "Please ensure it's not a scanned image."
                )
            
            print(f"✅ Extracted {len(full_text)} characters")
            return full_text
            
        except Exception as e:
            raise Exception(f"PDF extraction failed: {str(e)}")
    
    def create_chunks(self, text: str) -> list[Document]:
        """Create text chunks with strict limits."""
        try:
            print("✂️ Creating text chunks...")
            
            # Create document
            documents = [Document(page_content=text)]
            
            # Split into chunks
            chunks = self.text_splitter.split_documents(documents)
            
            print(f"📦 Created {len(chunks)} chunks")
            
            # Apply hard limit
            if len(chunks) > MAX_CHUNKS:
                print(f"⚠️ Limiting to {MAX_CHUNKS} chunks (memory constraint)")
                chunks = chunks[:MAX_CHUNKS]
            
            # Clean up
            del documents
            gc.collect()
            
            print(f"✅ Final: {len(chunks)} chunks ready")
            return chunks
            
        except Exception as e:
            raise Exception(f"Chunk creation failed: {str(e)}")
    
    def get_text_stats(self, text: str) -> dict:
        """Get statistics about extracted text."""
        return {
            "total_chars": len(text),
            "total_words": len(text.split()),
            "total_lines": len(text.split("\n"))
        }