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


class FactCheckerAgent:
    """AI agent responsible for checking claims against source evidence."""

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

    def check_claims(self, claims, sources):
        """Check claims against the supplied source text."""

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

        claims_text = "\n".join(
            f"{index + 1}. {claim}"
            for index, claim in enumerate(claims)
        )

        prompt = f"""
You are a careful fact-checking research assistant.

Your task is to evaluate the claims below ONLY against the supplied
source material.

Claims:
{claims_text}

Source material:
{source_text}

For every claim, provide:

1. Claim
2. Verification Status
3. Evidence
4. Supporting Source

Allowed verification statuses:
- SUPPORTED
- PARTIALLY SUPPORTED
- NOT SUPPORTED
- INSUFFICIENT EVIDENCE

Important rules:
- Do not use information that is not contained in the supplied sources.
- Do not invent evidence or sources.
- If the sources do not contain enough information, use
  INSUFFICIENT EVIDENCE.
- Keep the distinction between evidence and interpretation clear.
"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        return response.text