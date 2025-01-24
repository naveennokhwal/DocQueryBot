__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import os
import tempfile
import streamlit as st
from dotenv import load_dotenv
from models.agent import Agent  # Assuming this is the same Agent class from your original code

# Load environment variables
load_dotenv()

class PDFChatApp:
    def __init__(self):
        # Set up temporary directory for PDF storage
        self.TEMP_PDF_DIR = tempfile.mkdtemp()
        self.current_pdf_path = None
        
        # Streamlit page configuration
        st.set_page_config(page_title="DocQueryBot", page_icon=":books:")
        
    def run(self):
        st.title("DocQueryBot")
        
        # API Key Input
        self.handle_api_key_input()
        
        # PDF Upload
        self.handle_pdf_upload()
        
        # Chat Interface
        self.handle_chat_interface()
    
    def handle_api_key_input(self):
        """Handle API key input with default key option"""
        st.sidebar.header("API Key Configuration")
        
        # Checkbox for default key
        use_default_key = st.sidebar.checkbox("Use Default Key", 
                                              help="Use the default key stored in .env")
        
        if use_default_key:
            # Try to get default key from environment
            default_key = os.getenv('GOOGLE_API_KEY')
            if default_key:
                st.sidebar.success("Default key loaded successfully")
                st.session_state['api_key'] = default_key
            else:
                st.sidebar.error("No default key found in .env")
        else:
            # Manual key input
            api_key = st.sidebar.text_input("Enter Gemini API Key", 
                                            type="password",
                                            help="Your personal Gemini API key")
            if api_key:
                st.session_state['api_key'] = api_key
    
    def handle_pdf_upload(self):
        """Handle PDF file upload"""
        st.sidebar.header("PDF Upload")
        uploaded_file = st.sidebar.file_uploader("Choose a PDF file", 
                                                 type=['pdf'])
        
        if uploaded_file is not None:
            # Save uploaded file to temp directory
            temp_path = os.path.join(self.TEMP_PDF_DIR, uploaded_file.name)
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            
            self.current_pdf_path = temp_path
            st.sidebar.success(f"Uploaded: {uploaded_file.name}")
    
    def handle_chat_interface(self):
        """Manage chat interactions"""
        # Validate PDF and API key before chat
        if not self.current_pdf_path:
            st.warning("Please upload a PDF first")
            return
        
        if 'api_key' not in st.session_state:
            st.warning("Please provide an API key")
            return
        
        # Chat input
        user_question = st.text_input("Ask a question about the PDF")
        
        if user_question:
            try:
                # Initialize Agent with current PDF and API key
                model = Agent(pdf_path=self.current_pdf_path, 
                              api_key=st.session_state['api_key'])
                
                # Generate and display answer
                answer = model.get_answer(user_question)
                st.write("**Answer:**", answer)
            
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

def main():
    app = PDFChatApp()
    app.run()

if __name__ == "__main__":
    main()
