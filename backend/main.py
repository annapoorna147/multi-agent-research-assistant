
import json
import logging
import os
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from pydantic import BaseModel, Field

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Multi-Agent Research Assistant",
    description="AI-powered research assistant API",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ResearchRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    mode: Literal["Quick", "Standard", "Deep"] = "Standard"


def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "YOUR_ACTUAL_API_KEY":
        raise HTTPException(
            status_code=503,
            detail="Gemini API key is not configured. Check the local .env file.",
        )
    return genai.Client(api_key=api_key)


@app.get("/")
def root():
    return {
        "name": "Multi-Agent Research Assistant",
        "status": "online",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/api/health")
def api_health():
    key_configured = bool(os.getenv("GEMINI_API_KEY"))
    return {
        "status": "healthy",
        "service": "research-api",
        "ai_configured": key_configured,
    }


@app.post("/api/research/")
def prepare_research(request: ResearchRequest):
    question = request.question.strip()
    if len(question) < 3:
        raise HTTPException(
            status_code=422,
            detail="Please enter a research question with at least 3 characters.",
        )

    mode_instructions = {
        "Quick": "Give a concise overview and 3 key research questions.",
        "Standard": "Give a balanced overview, 4 key questions, and practical next steps.",
        "Deep": (
            "Give a detailed research framework, 6 key questions, "
            "methodological considerations, limitations, and next steps."
        ),
    }

    prompt = f"""
You are an academic research assistant.

Prepare a research brief for this question:
{question}

Research mode: {request.mode}
Instructions: {mode_instructions[request.mode]}

Return only valid JSON with exactly these keys:
- title: short descriptive title
- question: the user's research question
- mode: the selected mode
- summary: a clear overview of the topic, not a claim that web research was performed
- key_questions: an array of research questions
- next_steps: an array of useful investigation steps
- notice: a brief statement that web sources have not been independently retrieved or verified

Do not invent citations, URLs, or claims of having searched the web.
"""

    try:
        client = get_gemini_client()
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "temperature": 0.3,
            },
        )

        if not response.text:
            raise ValueError("Gemini returned an empty response.")

        result = json.loads(response.text)

        required_keys = {
            "title",
            "question",
            "mode",
            "summary",
            "key_questions",
            "next_steps",
            "notice",
        }
        if not required_keys.issubset(result):
            raise ValueError("Gemini response is missing required fields.")

        result["question"] = question
        result["mode"] = request.mode
        return result

    except HTTPException:
        raise
    except Exception:
        logger.exception("Gemini research generation failed")
        raise HTTPException(
            status_code=502,
            detail=(
                "The AI research request failed. Check the backend logs, "
                "API key, model availability, and API quota."
            ),
        )
