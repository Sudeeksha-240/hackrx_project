from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from PyPDF2 import PdfReader
import openai
import os
from typing import List
from io import BytesIO

# Load OpenAI API Key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

class RequestData(BaseModel):
    documents: str
    questions: List[str]

@app.get("/")
def read_root():
    return {"message": "HackRx LLM Query API. Go to /docs for Swagger UI."}

@app.post("/api/v1/hackrx/run")
def run_query(data: RequestData):
    try:
        # Download the PDF
        response = requests.get(data.documents)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Unable to fetch PDF")

        # Read PDF contents
        pdf = PdfReader(BytesIO(response.content))
        text = ""
        for page in pdf.pages:
            text += page.extract_text() or ""

        if not text.strip():
            raise HTTPException(status_code=400, detail="PDF content is empty")

        # Prepare messages for GPT-4
        system_prompt = (
            "You are an assistant reading an insurance policy document. "
            "Answer the user's questions using only the given content. "
            "Be concise, accurate, and only refer to content from the document."
        )

        messages = [{"role": "system", "content": system_prompt}]
        q_and_a = []
        for question in data.questions:
            messages.append({"role": "user", "content": f"Document:\n{text}\n\nQuestion: {question}"})
            completion = openai.ChatCompletion.create(
                model="gpt-4",
                messages=messages,
                temperature=0.3
            )
            answer = completion.choices[0].message["content"].strip()
            q_and_a.append(answer)
            messages.pop()  # Reset for the next question

        return {"answers": q_and_a}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
