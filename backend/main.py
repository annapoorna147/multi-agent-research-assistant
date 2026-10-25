import logging
import os
from urllib.parse import urlparse

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Multi-Agent Research Assistant",
    description="AI research API with Google Search grounding",
    version="2.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ResearchRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    mode: str = "Standard"


def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "YOUR_ACTUAL_API_KEY":
        raise HTTPException(
            status_code=503,
            detail="Gemini API key is not configured. Check the local .env file.",
        )
    return genai.Client(api_key=api_key)


def get_attr(obj, name, default=None):
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


def extract_grounding(response):
    candidates = get_attr(response, "candidates", []) or []
    candidate = candidates[0] if candidates else None
    metadata = get_attr(candidate, "grounding_metadata")

    chunks = get_attr(metadata, "grounding_chunks", []) or []
    supports = get_attr(metadata, "grounding_supports", []) or []

    sources = []
    chunk_to_source = {}

    for chunk_index, chunk in enumerate(chunks):
        web = get_attr(chunk, "web")
        if not web:
            continue

        url = get_attr(web, "uri", "")
        title = get_attr(web, "title", "") or "Web source"

        if not isinstance(url, str) or not url.startswith("https://"):
            continue

        domain = urlparse(url).netloc
        source_index = len(sources)

        sources.append({
            "rank": source_index + 1,
            "title": title,
            "url": url,
            "domain": domain,
            "snippet": "Retrieved through Gemini Google Search grounding.",
            "recommendation": "Search-grounded source",
        })
        chunk_to_source[chunk_index] = source_index

    return sources, supports, chunk_to_source


def add_inline_citations(text, supports, chunk_to_source, sources):
    insertions = []

    for support in supports:
        segment = get_attr(support, "segment")
        end_index = get_attr(segment, "end_index")
        chunk_indices = get_attr(
            support, "grounding_chunk_indices", []
        ) or []

        if not isinstance(end_index, int) or not chunk_indices:
            continue

        links = []
        for chunk_index in chunk_indices:
            source_index = chunk_to_source.get(chunk_index)
            if source_index is not None:
                source = sources[source_index]
                links.append(
                    f"[{source_index + 1}]({source['url']})"
                )

        if links and 0 <= end_index <= len(text):
            insertions.append(
                (end_index, " (" + ", ".join(dict.fromkeys(links)) + ")")
            )

    # Insert from right to left so original text offsets remain valid.
    for position, citation in sorted(insertions, reverse=True):
        text = text[:position] + citation + text[position:]

    return text


def run_research(question, mode):
    mode_instructions = {
        "Quick": (
            "Write a concise overview, identify 3 key questions, "
            "and prioritize the most useful findings."
        ),
        "Standard": (
            "Write a balanced report with an overview, 4 key questions, "
            "major findings, limitations, and practical next steps."
        ),
        "Deep": (
            "Write a detailed research report with 6 key questions, "
            "methodological considerations, competing perspectives, "
            "limitations, and actionable next steps."
        ),
    }

    prompt = f"""
You are a careful research assistant. Use Google Search to investigate
the user's question and ground factual claims in retrieved web sources.

Research question:
{question}

Research depth: {mode}
Instructions: {mode_instructions[mode]}

Write a readable Markdown report with these sections:
## Overview
## Key findings
## Questions to investigate
## Limitations and uncertainties
## Next steps

Prioritize relevant primary sources, official documentation, research
papers, and reputable organizations when available. Distinguish established
facts from interpretation. Do not invent source titles, URLs, statistics,
or quotations. If evidence is insufficient or sources disagree, say so.
Do not claim that every claim has been independently fact-checked.
"""

    client = get_gemini_client()

    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-3.8-flash"),
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())],
            temperature=0.3,
        ),
    )

    report = response.text
    if not report:
        raise ValueError("Gemini returned an empty response.")

    sources, supports, chunk_to_source = extract_grounding(response)
    report = add_inline_citations(
        report, supports, chunk_to_source, sources
    )

    grounded = bool(sources)

    result = {
        "final_report": report,
        "best_sources": sources,
        "analysis": (
            "The report was generated using Gemini with Google Search "
            "grounding. Review the cited source pages directly before "
            "relying on important claims."
        ),
        "fact_checking": (
            "Google Search grounding supplied the sources shown above. "
            "This does not constitute an independent, claim-by-claim "
            "fact-check."
        ),
        "evidence": {
            "summary": {
                "total_claims": None,
                "evidence_coverage_rate": None,
                "strong": None,
                "weak": None,
                "unsupported_claims": None,
            }
        },
        "contradictions": {
            "summary": {
                "overall_status": "Not independently assessed",
                "contradictions": None,
                "uncertainties": None,
                "agreements": None,
            }
        },
        "notice": (
            "Google Search grounding returned sources."
            if grounded
            else (
                "No grounding sources were returned for this response. "
                "Treat the report as unverified and retry if needed."
            )
        ),
    }

    return {
        "status": "completed",
        "question": question,
        "mode": mode,
        "result": result,
    }


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
async def prepare_research(request: ResearchRequest):
    question = request.question.strip()
    mode = request.mode.strip().title()

    if len(question) < 3:
        raise HTTPException(
            status_code=422,
            detail="Please enter a research question with at least 3 characters.",
        )

    if mode not in {"Quick", "Standard", "Deep"}:
        raise HTTPException(
            status_code=422,
            detail="Mode must be Quick, Standard, or Deep.",
        )

    try:
        return await run_in_threadpool(run_research, question, mode)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Grounded research generation failed")

        error_text = str(exc).lower()
        error_code = getattr(exc, "code", None)
        if error_code is None:
            error_code = getattr(exc, "status_code", None)

        if error_code == 429 or "429" in error_text or "resource_exhausted" in error_text or "quota exceeded" in error_text or "too many requests" in error_text:
            raise HTTPException(
                status_code=429,
                detail="The Gemini API quota or rate limit was reached. Check Google AI Studio usage and rate limits before retrying.",
            ) from exc

        if error_code == 503 or "503" in error_text or "unavailable" in error_text:
            raise HTTPException(
                status_code=503,
                detail="The AI service is temporarily unavailable. Please retry shortly.",
            ) from exc

        raise HTTPException(
            status_code=502,
            detail="The upstream research request failed. Check the backend logs for the underlying error.",
        ) from exc
