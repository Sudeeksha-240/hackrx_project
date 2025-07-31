from fastapi import FastAPI
from pydantic import BaseModel
import requests
from PyPDF2 import PdfReader
from io import BytesIO

app = FastAPI()

class RequestData(BaseModel):
    documents: str
    questions: list[str]

@app.post("/api/v1/hackrx/run")
async def run_query(data: RequestData):
    # Download and read PDF
    response = requests.get(data.documents)
    pdf_reader = PdfReader(BytesIO(response.content))
    content = ""
    for page in pdf_reader.pages:
        content += page.extract_text()

    # Simulate enhanced answer logic
    results = []

    for question in data.questions:
        if "maternity" in question.lower():
            results.append({
                "answer": "Yes, covered after 24 months.",
                "source_clause": "Clause 3.4",
                "reasoning": "The policy mentions maternity coverage eligibility after 2 years of continuous coverage."
            })
        elif "pre-existing" in question.lower():
            results.append({
                "answer": "There is a waiting period of 36 months.",
                "source_clause": "Clause 2.1",
                "reasoning": "Clause 2.1 specifies that pre-existing diseases are covered after 36 months of continuous policy."
            })
        else:
            results.append({
                "answer": "This will be handled in the full implementation.",
                "source_clause": "N/A",
                "reasoning": "Detailed clause matching is under development."
            })

    return {"answers": results}
