from fastapi import FastAPI, Header
from pydantic import BaseModel
from typing import List
import requests
import io
import PyPDF2

app = FastAPI()

# Request schema
class QueryRequest(BaseModel):
    documents: str  # URL to PDF
    questions: List[str]

# Response schema
class QueryResponse(BaseModel):
    answers: List[str]

# Endpoint as required by HackRx: /hackrx/run
@app.post("/hackrx/run", response_model=QueryResponse)
async def run_query(data: QueryRequest, authorization: str = Header(None)):
    # Download PDF from URL
    try:
        pdf_response = requests.get(data.documents)
        pdf_response.raise_for_status()
        pdf_stream = io.BytesIO(pdf_response.content)
    except Exception as e:
        return {"answers": [f"Error fetching PDF: {str(e)}"] * len(data.questions)}

    # Extract text from PDF
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_stream)
        full_text = ""
        for page in pdf_reader.pages:
            full_text += page.extract_text()
    except Exception as e:
        return {"answers": [f"Error reading PDF: {str(e)}"] * len(data.questions)}

    # Placeholder logic: return mock answers (you can integrate GPT or RAG here)
    answers = []
    for question in data.questions:
        answer = f"Answer to: '{question}' — based on extracted content length {len(full_text)}"
        answers.append(answer)

    return {"answers": answers}
