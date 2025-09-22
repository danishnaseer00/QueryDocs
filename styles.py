def get_custom_css():
    return """
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Main app styling */
    .stApp {
        background: linear-gradient(135deg, #0c0c0c 0%, #1a1a1a 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Header styling */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        border-bottom: 1px solid #333;
        margin-bottom: 2rem;
    }
    
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
    }
    
    .main-subtitle {
        color: #888;
        font-size: 1.1rem;
        font-weight: 400;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: #111 !important;
        border-right: 1px solid #333;
    }
    
    .sidebar-content {
        padding: 1rem;
    }
    
    /* File uploader styling */
    .stFileUploader > div {
        background: #222;
        border: 2px dashed #444;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
    }
    
    .stFileUploader > div:hover {
        border-color: #667eea;
        background: #2a2a2a;
    }
    
    /* Chat container */
    .chat-container {
        background: #1a1a1a;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid #333;
    }
    
    /* Message styling */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 18px 18px 5px 18px;
        margin: 0.5rem 0;
        margin-left: 20%;
        box-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
    }
    
    .bot-message {
        background: #2a2a2a;
        color: #e0e0e0;
        padding: 1rem 1.5rem;
        border-radius: 18px 18px 18px 5px;
        margin: 0.5rem 0;
        margin-right: 20%;
        border-left: 3px solid #667eea;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
    }
    
    .pdf-response {
        border-left-color: #4CAF50;
    }
    
    .general-response {
        border-left-color: #FF9800;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.7rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* Text input styling */
    .stTextInput > div > div > input {
        background: #2a2a2a;
        border: 1px solid #444;
        border-radius: 8px;
        color: white;
        padding: 0.7rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 1px #667eea;
    }
    
    /* Success/Error messages */
    .stSuccess {
        background: #1a4a3a;
        border: 1px solid #4CAF50;
        color: #4CAF50;
    }
    
    .stError {
        background: #4a1a1a;
        border: 1px solid #f44336;
        color: #f44336;
    }
    
    /* Status indicator */
    .status-indicator {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-pdf {
        background: #4CAF50;
    }
    
    .status-general {
        background: #FF9800;
    }
    
    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """