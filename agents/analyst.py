import os

import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()


def get_api_key():
    """Get the Gemini API key from Streamlit secrets or local .env."""

    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        api_key = None

    return api_key or os.getenv("GEMINI_API_KEY")


class AnalystAgent:
    """AI agent responsible for analyzing findings across sources."""

    def __init__(self):
        api_key = get_api_key()

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not set."
            )

        self.client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=120000),
        )

        self.model = "gemini-3.1-flash-lite"

    def analyze(self, question, sources):
        """Analyze findings across research sources."""

        source_text = "\n\n".join(
            [
                (
                    f"Source {index + 1}\n"
                    f"Title: {source.get('title', '')}\n"
                    f"URL: {source.get('url', '')}\n"
                    f"Content: {source.get('text', '')[:12000]}"
                )
                for index, source in enumerate(sources)
                if source.get("success") and source.get("text")
            ]
        )

        prompt = f"""
You are an analytical research assistant.

Analyze the supplied research sources in relation to the research question.

Research question:
{question}

Source material:
{source_text}

Return your analysis using these sections:

1. Common Themes
2. Differences Between Sources
3. Contradictions or Uncertainties
4. Relationships Between Findings
5. Key Insights
6. Evidence vs Interpretation

Important rules:
- Use only the supplied source material.
- Do not invent facts or sources.
- Clearly distinguish evidence from interpretation.
- If the sources do not provide enough information, say so.
"""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )

            if not response or not response.text:
                return (
                    "ANALYSIS TEMPORARILY UNAVAILABLE\n\n"
                    "The analysis agent returned an empty response. "
                    "The available research sources can still be used "
                    "for evidence and source comparison."
                )

            return response.text.strip()

        except Exception as error:
            message = str(error).lower()

            if (
                "503" in message
                or "unavailable" in message
                or "high demand" in message
                or "429" in message
                or "resource exhausted" in message
                or "rate limit" in message
            ):
                return (
                    "ANALYSIS TEMPORARILY UNAVAILABLE\n\n"
                    "The analysis AI service is temporarily unavailable "
                    "or rate-limited. The research pipeline continued "
                    "using the available source evidence.\n\n"
                    f"Service detail: {error}"
                )

            raise