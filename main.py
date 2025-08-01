from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import requests
from PyPDF2 import PdfReader
import io

app = FastAPI()

# Request schema
class QueryRequest(BaseModel):
    documents: str  # URL to the PDF
    questions: list[str]

# Response schema
class QueryResponse(BaseModel):
    answers: list[str]

# Root endpoint to redirect to Swagger UI
@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")

# PDF extraction function
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

# Dummy answer generator function
def dummy_answer_engine(text: str, questions: list[str]) -> list[str]:
    return [f"This is a dummy answer for: {q}" for q in questions]

# Endpoint to process the questions based on PDF content
@app.post("/api/v1/hackrx/run", response_model=QueryResponse)
def run_query(request: QueryRequest):
    text = extract_text_from_pdf_url(request.documents)
    answers = dummy_answer_engine(text, request.questions)
    return {"answers": answers}

@app.post("/api/v1/hackrx/run", response_model=QueryResponse)
def run_query(request: QueryRequest):
    try:
        text = extract_text_from_pdf_url(request.documents)
        if not text.strip():
            raise HTTPException(status_code=400, detail="Extracted text is empty")
        answers = dummy_answer_engine(text, request.questions)
        return {"answers": answers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

