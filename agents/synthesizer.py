import os
from typing import Any

import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()


def get_api_key() -> str | None:
    """Get the Gemini API key from Streamlit secrets or local .env."""

    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        api_key = None

    return api_key or os.getenv("GEMINI_API_KEY")


class SynthesizerAgent:
    """
    AI agent responsible for creating the final
    evidence-grounded research report.
    """

    def __init__(self) -> None:
        api_key = get_api_key()

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not set."
            )

        self.client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(
                timeout=120000,
            ),
        )

        self.model = "gemini-3.1-flash-lite"

    @staticmethod
    def _format_sources(
        sources: list[dict[str, Any]],
    ) -> str:
        """Format ranked sources for the synthesis prompt."""

        formatted_sources = []

        for index, source in enumerate(sources):
            title = source.get("title", "Untitled source")
            url = source.get("url", "")
            domain = source.get("domain", "")
            snippet = source.get("snippet", "")
            text = source.get("text", "")

            content = text or snippet

            if len(content) > 8000:
                content = content[:8000]

            formatted_sources.append(
                (
                    f"Source {index + 1}\n"
                    f"Title: {title}\n"
                    f"Domain: {domain}\n"
                    f"URL: {url}\n"
                    f"Content:\n{content}"
                )
            )

        return "\n\n".join(formatted_sources)

    @staticmethod
    def _format_best_sources(
        best_sources: list[dict[str, Any]],
    ) -> str:
        """Format the highest-ranked sources."""

        if not best_sources:
            return "No best sources were identified."

        formatted = []

        for index, source in enumerate(best_sources):
            formatted.append(
                (
                    f"Best Source {index + 1}\n"
                    f"Title: {source.get('title', '')}\n"
                    f"Domain: {source.get('domain', '')}\n"
                    f"URL: {source.get('url', '')}\n"
                    f"Score: {source.get('overall_score', '')}\n"
                    f"Recommendation: "
                    f"{source.get('recommendation', '')}"
                )
            )

        return "\n\n".join(formatted)

    @staticmethod
    def _format_evidence(
        evidence: dict[str, Any] | None,
    ) -> str:
        """Format evidence intelligence output."""

        if not evidence:
            return "No evidence intelligence was provided."

        summary = evidence.get("summary", {})
        claims = evidence.get("claims", [])
        evidence_map = evidence.get("evidence_map", [])
        citations = evidence.get("citations", [])

        sections = [
            "Evidence Summary:",
            str(summary),
            "",
            "Claims:",
        ]

        for claim in claims:
            sections.append(
                (
                    f"- {claim.get('claim_id', '')}: "
                    f"{claim.get('claim', '')}"
                )
            )

        sections.append("")
        sections.append("Claim-to-Evidence Mapping:")

        for item in evidence_map:
            sections.append(
                (
                    f"- Claim: {item.get('claim_id', '')}\n"
                    f"  Strength: {item.get('strength', '')}\n"
                    f"  Evidence: {item.get('evidence', [])}"
                )
            )

        sections.append("")
        sections.append("Citation Records:")

        for citation in citations:
            sections.append(
                f"- {citation}"
            )

        return "\n".join(sections)

    @staticmethod
    def _format_contradictions(
        contradictions: dict[str, Any] | None,
    ) -> str:
        """Format contradiction analysis."""

        if not contradictions:
            return "No contradiction analysis was provided."

        summary = contradictions.get("summary", {})

        contradiction_items = contradictions.get(
            "contradictions",
            [],
        )

        uncertainty_items = contradictions.get(
            "uncertainties",
            [],
        )

        agreement_items = contradictions.get(
            "agreements",
            [],
        )

        sections = [
            "Contradiction Summary:",
            str(summary),
            "",
            "Contradictions:",
        ]

        if contradiction_items:
            for item in contradiction_items:
                sections.append(
                    (
                        f"- {item.get('first_source', '')} vs "
                        f"{item.get('second_source', '')}: "
                        f"{item.get('first_claim', '')} / "
                        f"{item.get('second_claim', '')}"
                    )
                )
        else:
            sections.append(
                "- No direct contradictions detected."
            )

        sections.append("")
        sections.append("Uncertainties:")

        if uncertainty_items:
            for item in uncertainty_items:
                sections.append(
                    (
                        f"- {item.get('first_source', '')} vs "
                        f"{item.get('second_source', '')}: "
                        f"{item.get('first_claim', '')} / "
                        f"{item.get('second_claim', '')}"
                    )
                )
        else:
            sections.append(
                "- No major uncertainty relationships detected."
            )

        sections.append("")
        sections.append("Agreements:")

        if agreement_items:
            for item in agreement_items:
                sections.append(
                    (
                        f"- {item.get('first_source', '')} and "
                        f"{item.get('second_source', '')}"
                    )
                )
        else:
            sections.append(
                "- No strong cross-source agreements detected."
            )

        return "\n".join(sections)

    @staticmethod
    def _format_fact_check(
        fact_check: Any,
    ) -> str:
        """Format fact-check results."""

        if not fact_check:
            return "No fact-check results were provided."

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

The final answer must be a research report, not a
description of your process.
"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        if not response or not response.text:
            raise RuntimeError(
                "Synthesizer returned an empty response."
            )

        return response.text.strip()