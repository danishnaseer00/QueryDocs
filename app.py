import streamlit as st
import os
from pdf_processor import PDFProcessor
from vector_store import VectorStore
from rag_chain import RAGChain
from styles import get_custom_css

# Page configuration
st.set_page_config(
    page_title="PDF Chat Assistant",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Force sidebar to be visible
st.sidebar.empty()

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "pdf_uploaded" not in st.session_state:
    st.session_state.pdf_uploaded = False
if "rag_chain" not in st.session_state:
    st.session_state.rag_chain = None

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">📄 PDF Chat Assistant</h1>
        <p class="main-subtitle">Upload a PDF and start a conversation with your document</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for PDF upload
    with st.sidebar:
        st.markdown("### 📤 Upload PDF Document")
        st.markdown("---")
        
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type="pdf",
            help="Upload a PDF document to start chatting with it"
        )
        
        if uploaded_file is not None:
            if st.button("🔄 Process PDF", type="primary"):
                process_pdf(uploaded_file)
        
        st.markdown("---")
        
        # Status indicator
        if st.session_state.pdf_uploaded:
            st.markdown("""
            <div style="color: #4CAF50; font-weight: 600;">
                <span class="status-indicator status-pdf"></span>
                PDF Ready for Chat
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="color: #FF9800; font-weight: 600;">
                <span class="status-indicator status-general"></span>
                No PDF Uploaded
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.experimental_rerun()
    
    # Main chat interface
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        # Chat container
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        # Display chat history
        if st.session_state.chat_history:
            for message in st.session_state.chat_history:
                if message["role"] == "user":
                    st.markdown(f"""
                    <div class="user-message">
                        <strong>You:</strong> {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    response_class = "pdf-response" if message["type"] == "pdf" else "general-response"
                    st.markdown(f"""
                    <div class="bot-message {response_class}">
                        <strong>Assistant:</strong> {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align: center; padding: 2rem; color: #666;">
                <h3>👋 Welcome to PDF Chat Assistant</h3>
                <p>Upload a PDF document and start asking questions about its content!</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Chat input
        with st.form(key="chat_form", clear_on_submit=True):
            question = st.text_input(
                "Ask a question about your PDF...",
                placeholder="Type your question here...",
                label_visibility="collapsed"
            )
            submit_button = st.form_submit_button("Send 📤")
        
        if submit_button and question:
            handle_chat(question)

def process_pdf(uploaded_file):
    """Process the uploaded PDF file."""
    try:
        with st.spinner("🔄 Processing PDF..."):
            # Initialize processors
            pdf_processor = PDFProcessor()
            vector_store = VectorStore()
            
            # Extract text from PDF
            text = pdf_processor.extract_text_from_pdf(uploaded_file)
            
            # Create chunks
            chunks = pdf_processor.create_chunks(text)
            
            # Create vector store
            vector_store.create_vectorstore(chunks)
            
            # Initialize RAG chain
            st.session_state.rag_chain = RAGChain()
            st.session_state.pdf_uploaded = True
            
            st.success("✅ PDF processed successfully! You can now start chatting.")
            
    except Exception as e:
        st.error(f"❌ Error processing PDF: {str(e)}")

def handle_chat(question):
    """Handle chat interaction."""
    if not st.session_state.pdf_uploaded:
        st.warning("⚠️ Please upload a PDF first!")
        return
    
    # Add user message to history
    st.session_state.chat_history.append({
        "role": "user",
        "content": question
    })
    
    try:
        with st.spinner("🤔 Thinking..."):
            # Get response from RAG chain
            response, response_type = st.session_state.rag_chain.answer_question(question)
            
            # Add assistant response to history
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response,
                "type": response_type
            })
            
        st.experimental_rerun()
        
    except Exception as e:
        st.error(f"❌ Error generating response: {str(e)}")

if __name__ == "__main__":
    # Check for Gemini API key
    if not os.getenv("GEMINI_API_KEY"):
        st.error("❌ Please set your GEMINI_API_KEY in the .env file")
        st.info("Create a .env file with: GEMINI_API_KEY=your_api_key_here")
        st.stop()
    
    main()