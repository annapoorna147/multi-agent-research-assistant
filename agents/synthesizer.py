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


class SynthesizerAgent:
    """AI agent responsible for creating the final research report."""

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

    def synthesize(self, question, sources, fact_check, analysis):
        """Create a final research report from all research outputs."""

        source_text = "\n\n".join(
            [
                (
                    f"Source {index + 1}\n"
                    f"Title: {source.get('title', '')}\n"
                    f"URL: {source.get('url', '')}\n"
                    f"Content: {source.get('text', '')[:10000]}"
                )
                for index, source in enumerate(sources)
                if source.get("success") and source.get("text")
            ]
        )

        prompt = f"""
You are a professional research report synthesizer.

Create a clear, structured final research report using ONLY the
research material supplied below.

Research question:
{question}

Source material:
{source_text}

Fact-check results:
{fact_check}

Analyst findings:
{analysis}

Return the report using these sections:

1. Research Question
2. Executive Summary
3. Key Findings
4. Evidence from Sources
5. Fact-Checked Claims
6. Analysis and Insights
7. Differences or Uncertainties
8. Conclusion
9. Sources

Important rules:

- Use only the supplied research material.
- Do not invent facts, sources, statistics, or citations.
- Keep evidence separate from interpretation.
- Clearly mention uncertainty when the sources do not provide enough
  evidence.
- Do not claim that information was independently verified.
- Preserve important differences between sources.
- Make the final report concise, readable, and well structured.
"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        return response.text