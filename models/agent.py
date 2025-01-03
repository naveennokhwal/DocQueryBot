from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file
api_key = os.getenv('GEMINI_API_KEY')

from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from .rag import RAGGemini


class Agent:
    def __init__(self, model_name="gemini-1.5-flash"):
        self.model_name = model_name
        self.model = None
        self.load_model()

    def load_model(self):
        """Load the Gemini model for text generation."""
        self.model = ChatGoogleGenerativeAI(model=self.model_name)
        return self.model

    def need_to_call(self):
        prompt = PromptTemplate(
            template= '''
                    You are an intelligent assistant. Use the following question to decide whether it is a conversation sentence or not.
                    if the sentence is a conversation then return "True" else "False". If you don't know the answer, return "False". Also if user ask about 
                    technical information then also you return "False".
                    Question: {question}
                    Answer: 
                    ''',
            input_variables= ['question']
        )

        chain = prompt | self.model | StrOutputParser()
        return chain
    
    def greeting(self):
        prompt = PromptTemplate(
            template= '''
                    You’re an intelligent assistant. Given a sentence, determine if it's a greeting. 
                    If it is, respond with a greeting and ask how you can help. If it's not a greeting, 
                    or if the question is technical, return "False".
                    Question: {question}
                    Answer: 
                    ''',
            input_variables= ['question']
        )

        chain = prompt | self.model | StrOutputParser()
        return chain 
    
    def get_answer(self, question):
        """Generate an answer based on the given question using the RAG chain."""
        conversation_chain = self.need_to_call()
        result = conversation_chain.invoke({"question": question})
        if  result[0:4] == "True":
            greeting_chain = self.greeting()
            response = greeting_chain.invoke({"question": question})
            if response[0:5] == "False":
                return "I’m a RAG system designed to provide information based on my existing database. Feel free to ask me questions about Chapter 11: Sound."
            else:
                return response
        elif result[0:5] == "False":
            rag_gemini_system = RAGGemini(
                data_dir=r"C:\Learning\Machine-Learning\Deep_Learning_WorkSpace\projects\chatbot\data\file\example.pdf", 
                vector_db_dir=r"C:\Learning\Machine-Learning\Deep_Learning_WorkSpace\projects\chatbot\data\vector_database", 
                model_name="gemini-1.5-flash", 
                embedding_model="models/embedding-001"
            )
            
            rag_gemini_system.load_vector_database()
            rag_gemini_system.load_model()

            rag_chain = rag_gemini_system.create_rag_chain()
            return rag_chain.invoke(question)
        else:
            return "Please make sure your query is correct!!!"