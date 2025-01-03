# DocQueryBot

**DocQueryBot** is a sophisticated chatbot system that leverages **LangChain**, **FastAPI**, and the **Google Gemini API** to answer questions from user-provided PDFs. It combines the power of Retrieval-Augmented Generation (RAG) with a novel distinction layer, ensuring efficient responses by differentiating between conversational queries and PDF-specific queries.

---

## Key Features

- **PDF-Based Querying**: Upload a PDF, and the bot will answer questions based on its content.
- **Distinction Layer**: Intelligent mechanism to differentiate between general conversational inputs (e.g., "Hi!") and PDF-related queries. This ensures that only relevant questions are directed to the vector database for processing.
- **Interactive UI**: Built using **FastAPI**, the project includes a user-friendly interface for seamless interaction with the chatbot.
- **Secure and Configurable**: API keys and sensitive information are securely managed using environment variables.

---

## Getting Started

### Prerequisites

- Python 3.8+
- A Google Gemini API key
- Required dependencies (see `requirements.txt`)

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/naveennokhwal/DocQueryBot.git
   cd DocQueryBot
   ```
2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv\Scripts\activate
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up your environment variables:
   ```bash
   cp .env.example .env  # copy the .env.example file to .env
   GEMINI_API_KEY=your_actual_api_key_here
   ```
### Usage
1. Start the FastAPI server:
   ```bash
   fastapi dev app/main.py
   ```
2. Open the interactive UI in your browser and start asking questions!

## Distinction Layer: Enhancing Efficiency
The distinction layer is a unique addition to this project. It ensures the chatbot efficiently handles both general conversation and PDF-specific queries by:
- *Avoiding unnecessary database lookups:* General queries like "Hi!" or "How are you?" are processed conversationally without searching the vector database.
- *Improving response times:* Only relevant queries trigger the expensive database and model processing.
This mechanism enhances the user experience and ensures optimal resource usage.

## Acknowledgments
- LangChain
- Google Gemini API
- FastAPI
