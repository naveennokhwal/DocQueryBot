import os
from dotenv import load_dotenv

load_dotenv()

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate

class RAGGemini:
    def __init__(self, data_dir, vector_db_dir, model_name="gemini-1.5-flash", 
                 embedding_model="models/embedding-001", api_key=None):
        self.data_dir = data_dir
        self.vector_db_dir = vector_db_dir
        self.model_name = model_name
        self.embedding_model = embedding_model
        self.api_key = api_key
        
        self.documents = []
        self.splits = []
        self.vectorstore = None
        self.model = None

    def load_documents(self):
        """Load PDF documents."""
        loader = PyPDFLoader(self.data_dir)
        self.documents = loader.load()
        return self.documents

    def split_documents(self, chunk_size=1000, chunk_overlap=200):
        """Split documents into manageable chunks."""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, 
            chunk_overlap=chunk_overlap
        )
        self.splits = text_splitter.split_documents(self.documents)
        return self.splits

    def load_vector_database(self):
        """Create vector database from document splits."""
        # Use API key for embeddings if provided
        embeddings = GoogleGenerativeAIEmbeddings(
            model=self.embedding_model,
            google_api_key=self.api_key if self.api_key else None
        )
        self.vectorstore = Chroma.from_documents(
            documents=self.splits, 
            embedding=embeddings, 
            persist_directory=self.vector_db_dir
        )
        return self.vectorstore

    def load_model(self):
        """Load Gemini model."""
        # Use API key if provided
        self.model = ChatGoogleGenerativeAI(
            model=self.model_name,
            google_api_key=self.api_key if self.api_key else None
        )
        return self.model

    def create_rag_chain(self):
        """Create RAG query chain."""
        retriever = self.vectorstore.as_retriever()
        prompt = PromptTemplate(
            template='''
            Use the provided context to answer the question precisely. 
            If the context doesn't contain the answer, say "I cannot find the answer in the document."
            
            Context: {context}
            Question: {question}
            Answer:
            ''',
            input_variables=['context', 'question']
        )

        rag_chain = (
            {"context": retriever | self.format_docs, "question": RunnablePassthrough()}
            | prompt
            | self.model
            | StrOutputParser()
        )
        return rag_chain

    def format_docs(self, docs):
        """Format retrieved documents."""
        return "\n\n".join(doc.page_content for doc in docs)