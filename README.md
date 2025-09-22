# QueryDocs

A professional RAG (Retrieval-Augmented Generation) application that allows you to upload PDF documents and have conversations with them using Google's Gemini AI.

## Features

- 📄 **PDF Upload & Processing**: Upload any PDF document for analysis
- 💬 **Intelligent Chat**: Ask questions about your PDF content
- 🎯 **Context-Aware Responses**: Gets answers directly from your document
- 🤖 **Fallback AI**: Handles general questions not covered in the PDF
- 🎨 **Professional Dark UI**: Clean, modern interface with Streamlit
- ⚡ **Fast Vector Search**: Uses ChromaDB for efficient document retrieval

## Architecture

- **Frontend**: Streamlit with custom dark theme
- **Vector Database**: ChromaDB for document storage and similarity search
- **Embeddings**: HuggingFace sentence-transformers
- **LLM**: Google Gemini Pro (free tier)
- **Framework**: LangChain for RAG implementation

## Installation

1. **Clone or create the project structure**:
```bash
mkdir pdf-chat-assistant
cd pdf-chat-assistant
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**:
```bash
# Copy the template
cp .env.template .env

# Edit .env and add your Gemini API key
GEMINI_API_KEY=your_gemini_api_key_here
```

4. **Get your free Gemini API key**:
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Add it to your `.env` file

## Usage

1. **Start the application**:
```bash
streamlit run app.py
```

2. **Upload a PDF**:
   - Use the sidebar to upload your PDF document
   - Click "Process PDF" to create the vector embeddings

3. **Start chatting**:
   - Ask questions about your PDF content
   - The system will indicate if answers come from the PDF or general AI knowledge

## Project Structure

```
pdf-chat-assistant/
├── app.py              # Main Streamlit application
├── config.py           # Configuration settings
├── pdf_processor.py    # PDF text extraction and chunking
├── vector_store.py     # ChromaDB vector store management
├── rag_chain.py        # RAG chain implementation with Gemini
├── styles.py           # Custom CSS styling
├── requirements.txt    # Python dependencies
├── .env.template       # Environment variables template
├── .env               # Your API keys (create this file)
└── chroma_db/         # ChromaDB storage (auto-created)
```

## How It Works

1. **PDF Processing**: Extracts text from uploaded PDF and splits into chunks
2. **Vector Storage**: Creates embeddings using sentence-transformers and stores in ChromaDB
3. **Question Processing**: Searches for relevant document chunks using similarity search
4. **Response Generation**: 
   - If relevant context found: Uses RAG with PDF context
   - If no relevant context: Falls back to general AI response
5. **UI Response**: Clearly indicates whether answer is from PDF or general knowledge

## Configuration

Key settings in `config.py`:
- `CHUNK_SIZE`: Size of text chunks (default: 1000)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 200) 
- `SIMILARITY_THRESHOLD`: Minimum similarity score (default: 0.7)

## API Usage

This application uses Google's Gemini Pro API (free tier) which includes:
- 15 requests per minute
- 1 million tokens per minute
- 1,500 requests per day

## Troubleshooting

**Common Issues:**

1. **API Key Error**: Make sure your `.env` file contains a valid Gemini API key
2. **PDF Processing Error**: Ensure your PDF is not password-protected or corrupted
3. **Memory Issues**: Large PDFs may require adjusting chunk size in `config.py`

**Dependencies Issues:**
```bash
# If you encounter ChromaDB issues on Windows:
pip install --upgrade chromadb

# If sentence-transformers fails:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

## License

This project is open source and available under the MIT License.