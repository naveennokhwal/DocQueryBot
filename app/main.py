import os
import tempfile
from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from models.agent import Agent

app = FastAPI()

# Initialize Jinja2Templates and static files
templates = Jinja2Templates(directory=r"C:\Learning\Machine-Learning\Deep_Learning_WorkSpace\projects\chatbot\app\templates")
app.mount("/static", StaticFiles(directory= r"C:\Learning\Machine-Learning\Deep_Learning_WorkSpace\projects\chatbot\app\static"), name="static")

# Temporary storage for uploaded files and API key
TEMP_PDF_DIR = tempfile.mkdtemp()
CURRENT_PDF_PATH = None
CURRENT_API_KEY = None

class PromptInput(BaseModel):
    prompt: str

class ResponseOutput(BaseModel):
    answer: str

@app.get("/", response_class=HTMLResponse)
async def get_homepage(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    global CURRENT_PDF_PATH
    
    # Ensure it's a PDF
    if not file.filename.lower().endswith('.pdf'):
        return JSONResponse(content={"error": "Only PDF files are allowed"}, status_code=400)
    
    # Save the uploaded PDF
    file_path = os.path.join(TEMP_PDF_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    
    CURRENT_PDF_PATH = file_path
    return JSONResponse(content={"message": "PDF uploaded successfully"})

@app.post("/set-api-key")
async def set_api_key(api_key: str = Form(...)):
    global CURRENT_API_KEY
    
    # Basic validation (optional)
    if not api_key or len(api_key) < 10:
        return JSONResponse(content={"error": "Invalid API key"}, status_code=400)
    
    CURRENT_API_KEY = api_key
    os.environ['GEMINI_API_KEY'] = api_key
    return JSONResponse(content={"message": "API key set successfully"})

@app.post("/ask", response_model=ResponseOutput)
async def generate_answer(prompt_input: PromptInput):
    global CURRENT_PDF_PATH, CURRENT_API_KEY
    
    # Check if PDF and API key are set
    if not CURRENT_PDF_PATH:
        return JSONResponse(content={"error": "No PDF uploaded"}, status_code=400)
    
    if not CURRENT_API_KEY:
        return JSONResponse(content={"error": "No API key provided"}, status_code=400)
    
    # Initialize Agent with current PDF
    model = Agent(pdf_path=CURRENT_PDF_PATH, api_key= CURRENT_API_KEY)
    
    # Generate answer
    answer = model.get_answer(prompt_input.prompt)
    return ResponseOutput(answer=answer)