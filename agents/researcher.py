import os

from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()


class ResearcherAgent:
    """AI agent responsible for creating a research brief."""

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not set. Add it to your .env file."
            )

        self.client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=120000),
        )

        self.model = "gemini-3.1-flash-lite"

    def research(self, question):
        prompt = f"""
You are a research assistant.

Analyze the following research question and create a structured research brief.

Research question:
{question}

Return the response with these sections:

1. Research Question
2. Short Overview
3. Key Areas to Investigate
4. Important Questions
5. Expected Research Focus

Do not claim that you searched the web or verified external sources.
This agent is currently responsible only for research planning and
initial knowledge generation.
"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        return response.text