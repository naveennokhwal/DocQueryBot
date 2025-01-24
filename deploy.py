__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import os
import tempfile
import streamlit as st
from models.agent import Agent
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Temporary storage for uploaded files and API key
TEMP_PDF_DIR = tempfile.mkdtemp()
CURRENT_PDF_PATH = None
CURRENT_API_KEY = None

# Streamlit app setup
st.set_page_config(page_title="DocQueryBot", layout="wide")
st.markdown("""
<style>
.stChatMessage {
    border-radius: 15px;
    padding: 10px;
    margin-bottom: 10px;
    max-width: 70%;
}
.stChatMessageUser {
    background-color: #007BFF;
    color: white;
    margin-left: auto;
    text-align: right;
}
.stChatMessageBot {
    background-color: #E9E9E9;
    color: black;
    margin-right: auto;
    text-align: left;
}
</style>
""", unsafe_allow_html=True)

st.title("DocQueryBot")
st.write("Interact with your PDF as if you're chatting with it. Upload a PDF, set your API key, and start the conversation.")

# File upload section
st.sidebar.header("Upload & Settings")
uploaded_file = st.sidebar.file_uploader("Upload a PDF", type=["pdf"])
if uploaded_file:
    # Save the uploaded PDF
    CURRENT_PDF_PATH = os.path.join(TEMP_PDF_DIR, uploaded_file.name)
    with open(CURRENT_PDF_PATH, "wb") as buffer:
        buffer.write(uploaded_file.read())
    st.sidebar.success(f"PDF uploaded successfully: {uploaded_file.name}")

# API key input section
use_default_key = st.sidebar.checkbox("Use Default API Key", value=True)
if use_default_key:
    CURRENT_API_KEY = DEFAULT_API_KEY
    st.sidebar.success("Using default API key.")
else:
    CURRENT_API_KEY = st.sidebar.text_input("Enter your API Key", type="password")
    if st.sidebar.button("Set API Key"):
        if not CURRENT_API_KEY or len(CURRENT_API_KEY) < 10:
            st.sidebar.error("Invalid API key. Please enter a valid key.")
        else:
            os.environ['GEMINI_API_KEY'] = CURRENT_API_KEY
            st.sidebar.success("API key set successfully.")

# Chat interface
st.subheader("Chat with DocQueryBot")
if not CURRENT_PDF_PATH:
    st.info("Please upload a PDF to start.")
elif not CURRENT_API_KEY:
    st.info("Please set an API key to start.")
else:
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history using containers
    with st.container():
        for speaker, message in st.session_state.chat_history:
            if speaker == "user":
                st.markdown(f'<div class="stChatMessage stChatMessageUser">{message}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="stChatMessage stChatMessageBot">{message}</div>', unsafe_allow_html=True)

    # Chat input at the bottom
    user_input = st.text_input("Type your question here:", key="chat_input", placeholder="Ask me anything about the PDF...")
    if st.button("Send", key="send_button"):
        if user_input.strip() == "":
            st.warning("Please enter a question.")
        else:
            # Display user message
            st.session_state.chat_history.append(("user", user_input))

            # Generate bot response
            try:
                model = Agent(pdf_path=CURRENT_PDF_PATH, api_key=CURRENT_API_KEY)
                answer = model.get_answer(user_input)
                st.session_state.chat_history.append(("bot", answer))
            except Exception as e:
                st.session_state.chat_history.append(("bot", f"An error occurred: {e}"))
