from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from vector_store import VectorStore
from config import GEMINI_API_KEY

class RAGChain:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=GEMINI_API_KEY,
            temperature=0.3
        )
        self.vector_store = VectorStore()
        
        # Custom prompt template for RAG
        self.rag_prompt_template = """
        You are an AI assistant that answers questions based on the provided PDF document context.
        
        Context from PDF: {context}
        
        Question: {question}
        
        Instructions:
        - Answer the question based ONLY on the information provided in the context from the PDF
        - If the question cannot be answered from the PDF context, respond with: "I cannot answer this question as it's not covered in the uploaded PDF document."
        - Be precise and cite relevant information from the document
        - Do not make up or assume information not present in the context
        
        Answer:
        """
        
        self.fallback_prompt_template = """
        You are a helpful AI assistant. The user asked a question that is not related to the PDF document they uploaded.
        
        Question: {question}
        
        Please provide a helpful and informative answer to this general question.
        
        Answer:
        """
    
    def setup_rag_chain(self):
        """Set up the RAG chain with retriever."""
        vectorstore = self.vector_store.load_vectorstore()
        if not vectorstore:
            return None
            
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        
        prompt = PromptTemplate(
            input_variables=["context", "question"],
            template=self.rag_prompt_template
        )
        
        chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": prompt}
        )
        
        return chain
    
    def answer_question(self, question: str):
        """Answer question using RAG or fallback to general AI."""
        # First, try to find relevant context from PDF
        relevant_docs = self.vector_store.similarity_search(question)
        
        if relevant_docs:
            # Use RAG chain for PDF-related questions
            rag_chain = self.setup_rag_chain()
            if rag_chain:
                response = rag_chain.run(question)
                return response, "pdf"
        
        # Fallback to general AI response
        fallback_prompt = PromptTemplate(
            input_variables=["question"],
            template=self.fallback_prompt_template
        )
        
        formatted_prompt = fallback_prompt.format(question=question)
        response = self.llm.invoke(formatted_prompt)
        
        return f"This question is not from the PDF. Here's a general answer:\n\n{response.content}", "general"