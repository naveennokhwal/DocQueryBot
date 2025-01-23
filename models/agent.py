from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables

from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from .rag import RAGGemini

class Agent:
    def __init__(self, pdf_path=None, model_name="gemini-1.5-flash", api_key=None):
        self.model_name = model_name
        self.pdf_path = pdf_path
        self.api_key = api_key
        self.model = None
        self.load_model()

    def load_model(self):
        """Load the Gemini model for text generation."""
        try:
            # Use explicitly provided API key
            if self.api_key:
                self.model = ChatGoogleGenerativeAI(
                    model=self.model_name, 
                    google_api_key=self.api_key
                )
            else:
                self.model = ChatGoogleGenerativeAI(model=self.model_name)
        except Exception as e:
            raise ValueError(f"Failed to load model: {e}")
        return self.model

    def need_to_call(self, question):
        """Determine if the question requires RAG or conversation handling."""
        prompt = PromptTemplate(
            template='''
                Classify the question type:
                - If it's a conversational or general query, return "CONVERSATION"
                - If it requires technical or specific information from the document, return "RAG"
                - If unsure, return "RAG"
                Question: {question}
                Classification:
            ''',
            input_variables=['question']
        )

        chain = prompt | self.model | StrOutputParser()
        return chain.invoke({"question": question})
    
    def greeting(self, question):
        greet_prompt = PromptTemplate(
            template= '''
                    You’re an intelligent assistant. Write a small greeting message in response to the given sentence.
                    and ask if they need any help. message should be concise.
                    Question: {question}
                    Answer: 
                    ''',
            input_variables= ['question']
        )

        chain = greet_prompt | self.model | StrOutputParser()
        return chain.invoke({"question": question})
     
    def get_answer(self, question):
        """Generate an answer based on the question type."""
        call_type = self.need_to_call(question)

        if call_type == "CONVERSATION":
            return self.greeting(question)
        
        if not self.pdf_path:
            return "Please upload a PDF first."

        # Initialize RAG system with the uploaded PDF and API key
        rag_system = RAGGemini(
            data_dir=self.pdf_path, 
            vector_db_dir=os.path.join(os.path.dirname(self.pdf_path), "vector_db"),
            model_name=self.model_name,
            api_key=self.api_key
        )
        
        rag_system.load_documents()
        rag_system.split_documents()
        rag_system.load_vector_database()
        rag_system.load_model()

        rag_chain = rag_system.create_rag_chain()
        return rag_chain.invoke(question)