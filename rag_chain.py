from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from vector_store import VectorStore
from config import GEMINI_API_KEY, LLM_TEMPERATURE, LLM_MAX_TOKENS


class RAGChain:
    def __init__(self):
        """Initialize RAG chain with optimized LLM settings."""
        print("🤖 Initializing Gemini model...")
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",  # Faster and cheaper than gemini-pro
            google_api_key=GEMINI_API_KEY,
            temperature=LLM_TEMPERATURE,
            max_output_tokens=LLM_MAX_TOKENS
        )
        self.vector_store = VectorStore()
        print("✅ RAG chain ready!")
        
        # Optimized RAG prompt
        self.rag_prompt_template = """You are a precise AI assistant analyzing a PDF document.

Context from PDF:
{context}

Question: {question}

Instructions:
- Answer ONLY using information from the context above
- Be concise and direct
- If the answer isn't in the context, say: "This information is not in the uploaded PDF."
- Cite specific details from the context

Answer:"""
        
        # Fallback prompt for general questions
        self.fallback_prompt_template = """Question: {question}

This question is not covered in the PDF. Provide a brief, helpful answer.

Answer:"""

    def answer_question(self, question: str):
        """Answer using RAG or fallback to general knowledge."""
        try:
            # Try to find relevant context
            relevant_docs = self.vector_store.similarity_search(question)
            
            if relevant_docs:
                # Use RAG with PDF context
                print("📄 Using PDF context...")
                response = self._answer_with_rag(question)
                return response, "pdf"
            else:
                # Fallback to general AI
                print("🌐 Using general knowledge...")
                response = self._answer_general(question)
                return response, "general"
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return f"Sorry, I encountered an error: {str(e)}", "general"

    def _answer_with_rag(self, question: str):
        """Answer using RAG chain with PDF context."""
        try:
            # Get retriever
            retriever = self.vector_store.get_retriever()
            if not retriever:
                return "PDF index not found. Please upload a PDF first."
            
            # Create prompt
            prompt = PromptTemplate(
                input_variables=["context", "question"],
                template=self.rag_prompt_template
            )
            
            # Create RAG chain
            chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=retriever,
                chain_type_kwargs={"prompt": prompt},
                return_source_documents=False  # Save memory
            )
            
            # Get response
            response = chain.invoke({"query": question})
            return response["result"]
            
        except Exception as e:
            print(f"❌ RAG error: {e}")
            return f"Error processing question: {str(e)}"

    def _answer_general(self, question: str):
        """Answer general questions without PDF context."""
        try:
            prompt = PromptTemplate(
                input_variables=["question"],
                template=self.fallback_prompt_template
            )
            
            formatted_prompt = prompt.format(question=question)
            response = self.llm.invoke(formatted_prompt)
            
            prefix = "ℹ️ This is a general answer (not from PDF):\n\n"
            return prefix + response.content
            
        except Exception as e:
            print(f"❌ General answer error: {e}")
            return "Sorry, I couldn't generate an answer."