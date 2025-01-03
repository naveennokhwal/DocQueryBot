from fastapi import FastAPI
from pydantic import BaseModel
from models.agent import Agent  # Import the RAGGemini class

from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

 
app = FastAPI()

# Initialize Jinja2Templates for rendering HTML
templates = Jinja2Templates(directory=r"C:\Learning\Machine-Learning\Deep_Learning_WorkSpace\projects\chatbot\app\templates")

# Mount the static folder to serve static files like CSS
app.mount("/static", StaticFiles(directory= r"C:\Learning\Machine-Learning\Deep_Learning_WorkSpace\projects\chatbot\app\templates\static"), name="static")

# Define input/output model for prompt
class PromptInput(BaseModel):
    prompt: str

class ResponseOutput(BaseModel):
    answer: str

# Initialize the Agent system
model = Agent()


# Serve the HTML page
@app.get("/", response_class=HTMLResponse)
async def get_homepage(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# API to generate answer for the query
@app.post("/ask", response_model=ResponseOutput)
async def generate_answer(prompt_input: PromptInput):
    prompt = prompt_input.prompt
    # Generate the answer using the RAG system
    answer = model.get_answer(prompt)
    return ResponseOutput(answer=answer)
