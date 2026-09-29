import os

from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()


class AnalystAgent:
    """AI agent responsible for analyzing findings from multiple sources."""

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

    def analyze(self, sources):
        """Analyze findings across multiple sources."""

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

Analyze the findings from the supplied sources.

Source material:
{source_text}

Return your analysis using these sections:

1. Common Themes
2. Key Findings
3. Differences Between Sources
4. Possible Contradictions
5. Important Relationships
6. Analytical Insights
7. Evidence vs Interpretation

Important rules:

- Use ONLY the supplied source material.
- Do not invent facts, sources, or evidence.
- Clearly distinguish evidence from interpretation.
- If the sources do not provide enough information, say so.
- Do not claim that you verified information outside the supplied sources.
- When identifying contradictions, explain exactly what differs.
- Keep the analysis structured and concise.
"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        return response.text