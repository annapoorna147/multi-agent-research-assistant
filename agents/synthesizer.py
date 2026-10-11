import os
from typing import Any

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
    """AI agent responsible for producing the final research report."""

    def __init__(self):
        api_key = get_api_key()

        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set.")

        self.client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=120000),
        )

        self.model = "gemini-3.1-flash-lite"

    @staticmethod
    def _format_sources(
        sources: list[dict[str, Any]],
    ) -> str:
        """Format all ranked research sources."""

        if not sources:
            return "No research sources were provided."

        formatted_sources = []

        for index, source in enumerate(sources, start=1):
            formatted_sources.append(
                f"""
Source {index}
-----------
Title: {source.get("title", "")}
URL: {source.get("url", "")}
Domain: {source.get("domain", "")}
Source Type: {source.get("source_type", "")}
Overall Score: {source.get("overall_score", "")}
Recommendation: {source.get("recommendation", "")}
Snippet: {source.get("snippet", "")}
Content:
{source.get("text", "")[:12000]}
""".strip()
            )

        return "\n\n".join(formatted_sources)

    @staticmethod
    def _format_best_sources(
        best_sources: list[dict[str, Any]],
    ) -> str:
        """Format the strongest sources selected by source intelligence."""

        if not best_sources:
            return "No best sources were selected."

        formatted_sources = []

        for index, source in enumerate(best_sources, start=1):
            formatted_sources.append(
                f"""
Best Source {index}
-----------------
Title: {source.get("title", "")}
URL: {source.get("url", "")}
Domain: {source.get("domain", "")}
Source Type: {source.get("source_type", "")}
Overall Score: {source.get("overall_score", "")}
Recommendation: {source.get("recommendation", "")}
Snippet: {source.get("snippet", "")}
""".strip()
            )

        return "\n\n".join(formatted_sources)

    @staticmethod
    def _format_evidence(
        evidence: dict[str, Any] | None,
    ) -> str:
        """Format evidence intelligence results."""

        if not evidence:
            return "No evidence intelligence was provided."

        summary = evidence.get("summary", {})
        claim_map = evidence.get("claim_evidence_map", [])

        formatted = [
            "Evidence Summary:",
            str(summary),
            "",
            "Claim-to-Evidence Mapping:",
        ]

        if claim_map:
            for item in claim_map:
                formatted.append(str(item))
        else:
            formatted.append("No claim-to-evidence mappings were provided.")

        return "\n".join(formatted)

    @staticmethod
    def _format_contradictions(
        contradictions: dict[str, Any] | None,
    ) -> str:
        """Format contradiction analysis results."""

        if not contradictions:
            return "No contradiction analysis was provided."

        summary = contradictions.get("summary", {})

        formatted = [
            "Contradiction Summary:",
            str(summary),
            "",
            "Agreements:",
            str(contradictions.get("agreements", [])),
            "",
            "Contradictions:",
            str(contradictions.get("contradictions", [])),
            "",
            "Uncertainties:",
            str(contradictions.get("uncertainties", [])),
        ]

        return "\n".join(formatted)

    @staticmethod
    def _format_fact_check(
        fact_check: Any,
    ) -> str:
        """Format fact-checking results."""

        if not fact_check:
            return "No fact-checking results were provided."

        return str(fact_check)

    @staticmethod
    def _format_analysis(
        analysis: Any,
    ) -> str:
        """Format analyst results."""

        if not analysis:
            return "No analyst findings were provided."

        return str(analysis)

    def synthesize(
        self,
        question: str,
        sources: list[dict[str, Any]],
        fact_check: Any,
        analysis: Any,
        evidence: dict[str, Any] | None = None,
        contradictions: dict[str, Any] | None = None,
        best_sources: list[dict[str, Any]] | None = None,
    ) -> str:
        """
        Create a final research report using:

        - ranked sources
        - best sources
        - evidence intelligence
        - contradiction analysis
        - fact checking
        - analyst findings
        """

        best_sources = best_sources or []

        source_text = self._format_sources(
            sources
        )

        best_source_text = self._format_best_sources(
            best_sources
        )

        evidence_text = self._format_evidence(
            evidence
        )

        contradiction_text = self._format_contradictions(
            contradictions
        )

        fact_check_text = self._format_fact_check(
            fact_check
        )

        analysis_text = self._format_analysis(
            analysis
        )

        prompt = f"""
You are the final research synthesis agent in a
multi-agent research system.

Your job is to create a rigorous, readable and
evidence-grounded research report.

RESEARCH QUESTION
=================
{question}

BEST-RANKED SOURCES
===================
{best_source_text}

ALL RESEARCH SOURCES
====================
{source_text}

EVIDENCE INTELLIGENCE
=====================
{evidence_text}

CONTRADICTION ANALYSIS
======================
{contradiction_text}

FACT-CHECK RESULTS
==================
{fact_check_text}

ANALYST FINDINGS
================
{analysis_text}

REPORT REQUIREMENTS
===================

Create the final report using exactly these sections:

1. Research Question

2. Executive Summary

3. Key Findings

4. Evidence

5. Source Comparison

6. Fact-Checked Claims

7. Contradictions and Uncertainties

8. Analysis and Insights

9. Conclusion

10. Sources and Citations

IMPORTANT RULES
===============

1. Use ONLY information contained in the supplied
   research material.

2. Do NOT invent facts, statistics, sources,
   citations, URLs or claims.

3. Do NOT use outside knowledge.

4. Evidence must be distinguished from interpretation.

5. When sources disagree, explicitly mention the
   disagreement instead of choosing a side without
   evidence.

6. When evidence is weak or insufficient, say so.

7. Do not describe a claim as confirmed merely because
   one source mentions it.

8. Prefer stronger and higher-ranked sources when
   summarizing evidence.

9. Preserve important uncertainty.

10. Do not claim independent verification.

11. Keep citations connected to the claims they support.

12. Make the report professional, concise and readable.

13. NEVER hide a detected contradiction.

14. If the structured contradiction analysis reports
    "Contradictions Detected", the final report MUST
    explicitly report those contradictions.

15. NEVER state that sources agree, are complementary,
    or are consistent when the structured contradiction
    analysis reports a contradiction.

16. The structured contradiction analysis takes priority
    over your own interpretation of whether two claims
    appear compatible.

17. Preserve the actual claims from both sources when
    reporting a contradiction.

18. Never fabricate a citation.

19. If the supplied material does not support a requested
    conclusion, clearly state that the evidence is
    insufficient.

20. Format the final report as Markdown.

21. Use Markdown headings, bullet lists and tables where
    they improve readability.

22. Keep source URLs visible in the Sources and Citations
    section.

The final answer must be a research report, not a
description of your process.
"""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )

            if not response or not response.text:
                raise RuntimeError(
                    "Synthesizer returned an empty response."
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
                    "# Research Report\n\n"
                    "## Research Synthesis Temporarily Unavailable\n\n"
                    "The research pipeline successfully collected and "
                    "analyzed the available sources, evidence, and "
                    "fact-checking information, but the final AI "
                    "synthesis service is temporarily unavailable.\n\n"
                    "The underlying research data is still available "
                    "in the sections below.\n\n"
                    "## Evidence\n\n"
                    f"{evidence_text}\n\n"
                    "## Contradiction Analysis\n\n"
                    f"{contradiction_text}\n\n"
                    "## Fact-Checked Claims\n\n"
                    f"{fact_check_text}\n\n"
                    "## Analysis and Insights\n\n"
                    f"{analysis_text}\n\n"
                    "## Sources and Citations\n\n"
                    f"{best_source_text}"
                )

            raise