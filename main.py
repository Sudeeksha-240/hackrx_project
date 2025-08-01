from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import requests
from PyPDF2 import PdfReader
import io

app = FastAPI()

class QueryRequest(BaseModel):
    documents: str  # URL to the PDF
    questions: list[str]

class QueryResponse(BaseModel):
    answers: list[str]

def extract_text_from_pdf_url(url: str) -> str:
    try:
        response = requests.get(url)
        response.raise_for_status()
        pdf_file = io.BytesIO(response.content)
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")

def dummy_answer_engine(text: str, questions: list[str]) -> list[str]:
    # Replace this with your real LLM logic
    return [f"Simulated answer for: {q}" for q in questions]

@app.post("/api/v1/hackrx/run", response_model=QueryResponse)
def run_query(request: QueryRequest):
    text = extract_text_from_pdf_url(request.documents)
    answers = dummy_answer_engine(text, request.questions)
    return {"answers": answers}

@app.get("/")
def root():
    return {"message": "HackRx LLM Query API. Go to /docs for Swagger UI."}
