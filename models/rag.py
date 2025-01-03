from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file
api_key = os.getenv('GEMINI_API_KEY')

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate

class RAGGemini:
    def __init__(self, data_dir, vector_db_dir, model_name="gemini-1.5-flash", embedding_model="models/embedding-001"):
        self.data_dir = data_dir
        self.vector_db_dir = vector_db_dir
        self.model_name = model_name
        self.embedding_model = embedding_model
        self.documents = []
        self.splits = []
        self.vectorstore = None
        self.model = None

        self.load_documents()
        self.split_documents()

    def load_documents(self):
        loader = PyPDFLoader(self.data_dir)
        docs = loader.load()
        self.documents.extend(docs)
        return self.documents

    def split_documents(self, chunk_size=1000, chunk_overlap=200):
        """Split the loaded documents into chunks for vector embedding."""
        if not self.documents:
            raise ValueError("No documents found. Load documents first.")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self.splits = text_splitter.split_documents(self.documents)
        return self.splits

    def load_vector_database(self):
        """Create or load a vector database from document splits."""
        if not self.splits:
            raise ValueError("No document splits found. Split documents first.")
        embeddings = GoogleGenerativeAIEmbeddings(model=self.embedding_model)
        self.vectorstore = Chroma.from_documents(documents=self.splits, embedding=embeddings, persist_directory=self.vector_db_dir)
        return self.vectorstore

    def load_model(self):
        """Load the Gemini model for text generation."""
        self.model = ChatGoogleGenerativeAI(model=self.model_name)
        return self.model

    def create_rag_chain(self):
        """Create and return the RAG chain for querying."""
        if not self.vectorstore or not self.model:
            raise ValueError("Ensure that the vectorstore and model are loaded before creating the RAG chain.")
        
        retriever = self.vectorstore.as_retriever()
        prompt = PromptTemplate(
            template='''
                    You are an assistant for question-answering tasks. Use the following pieces of retrieved context to
                    answer the question.If you don't know the answer, just say that you don't know. Use three sentences
                    maximum and keep the answer concise.
                    Question: {question} 
                    Context: {context} 
                    Answer:
                    '''
        )

        rag_chain = (
            {"context": retriever | self.format_docs, "question": RunnablePassthrough()}
            | prompt
            | self.model
            | StrOutputParser()
        )
        return rag_chain

    def format_docs(self, docs):
        """Helper method to format the retrieved documents for RAG."""
        return "\n\n".join(doc.page_content for doc in docs)
        
