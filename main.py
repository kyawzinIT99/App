from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional
import json
import os
import httpx

app = FastAPI()

# Load API key from environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise Exception("Set the GROQ_API_KEY environment variable")

# Correct Groq API endpoint (OpenAI-compatible)
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

DATA_FILE = "trip_data.json"

# -----------------------------
# Models
# -----------------------------
class Expense(BaseModel):
    date: str
    category: str
    amount: float
    description: Optional[str] = ""

class TripData(BaseModel):
    destination: str
    start_date: str
    end_date: str
    expenses: List[Expense] = []

# -----------------------------
# Helpers
# -----------------------------
def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# -----------------------------
# Trip Endpoints
# -----------------------------
@app.get("/trip_data")
def get_trip_data():
    return load_data()

@app.post("/trip_data")
def add_trip(trip: TripData):
    data = load_data()
    data.append(trip.dict())
    save_data(data)
    return {"message": "Trip added", "trip_index": len(data) - 1}

@app.post("/trip_data/{trip_index}/expense")
def add_expense(trip_index: int, expense: Expense):
    data = load_data()
    if trip_index < 0 or trip_index >= len(data):
        raise HTTPException(status_code=404, detail="Trip not found")
    data[trip_index]["expenses"].append(expense.dict())
    save_data(data)
    return {"message": "Expense added"}

@app.delete("/trip_data/{trip_index}/expense/{expense_index}")
def delete_expense(trip_index: int, expense_index: int):
    data = load_data()
    if trip_index < 0 or trip_index >= len(data):
        raise HTTPException(status_code=404, detail="Trip not found")
    if expense_index < 0 or expense_index >= len(data[trip_index]["expenses"]):
        raise HTTPException(status_code=404, detail="Expense not found")
    
    deleted = data[trip_index]["expenses"].pop(expense_index)
    save_data(data)
    return {"message": "Expense deleted", "deleted": deleted}


# -----------------------------
# AI Endpoint
# -----------------------------
@app.post("/ask_ai")
async def ask_ai(request: Request):
    json_body = await request.json()
    question = json_body.get("question")
    if not question:
        raise HTTPException(status_code=400, detail="Missing 'question' in request body")

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "llama-3.3-70b-versatile",  # ✅ pick one from your list
        "messages": [
            {"role": "system", "content": "You are a helpful trip planning assistant."},
            {"role": "user", "content": question},
        ],
        "temperature": 0.7,
        "max_completion_tokens": 512,  # <= must not exceed model limit
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(GROQ_API_URL, headers=headers, json=payload)
            response.raise_for_status()
    except httpx.HTTPError as e:
        return {
            "error": str(e),
            "status": getattr(e.response, "status_code", None),
            "body": getattr(e.response, "text", ""),
        }

    result = response.json()
    try:
        answer = result["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError):
        answer = "No valid response from Groq"

    return {"answer": answer}