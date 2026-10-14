
from typing import Any

from agents.analyst import AnalystAgent
from agents.fact_checker import FactCheckerAgent
from agents.researcher import ResearcherAgent
from agents.synthesizer import SynthesizerAgent
from tools.contradiction_detector import ContradictionDetector
from tools.evidence_intelligence import EvidenceIntelligence
from tools.source_extractor import SourceExtractor
from tools.source_intelligence import SourceIntelligence
from tools.web_search import search_web


class ResearchPipeline:
    """Orchestrate research while preventing unusable sources from becoming evidence."""

    def __init__(self) -> None:
        self.researcher = ResearcherAgent()
        self.source_extractor = SourceExtractor()
        self.source_intelligence = SourceIntelligence()
        self.evidence_intelligence = EvidenceIntelligence()
        self.contradiction_detector = ContradictionDetector()
        self.fact_checker = FactCheckerAgent()
        self.analyst = AnalystAgent()
        self.synthesizer = SynthesizerAgent()

    def _discover_sources(
        self,
        question: str,
        max_results: int,
    ) -> list[dict[str, Any]]:
        """Return search results with extraction status and diagnostics."""
        search_results = search_web(question, max_results=max_results)
        enriched_sources = []

        for result in search_results:
            url = result.get("url", "")
            if not url:
                continue

            try:
                extracted = self.source_extractor.extract(url)
            except Exception as exc:
                extracted = {
                    "text": "",
                    "success": False,
                    "error": f"Extraction failed: {exc}",
                }

            enriched_sources.append(
                {
                    "title": result.get("title", ""),
                    "url": url,
                    "snippet": result.get("snippet", ""),
                    "text": extracted.get("text", ""),
                    "success": extracted.get("success", False),
                    "error": extracted.get("error", ""),
                }
            )

        return enriched_sources

    @staticmethod
    def _usable_sources(
        sources: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Only allow successfully extracted article content into evidence analysis."""
        usable = []

        for source in sources:
            text = source.get("text", "")
            if (
                source.get("success") is True
                and isinstance(text, str)
                and len(text.strip()) >= SourceExtractor.MIN_CONTENT_LENGTH
            ):
                usable.append(source)

        return usable

    @staticmethod
    def _source_summary(
        sources: list[dict[str, Any]],
        usable_sources: list[dict[str, Any]],
    ) -> dict[str, int]:
        """Summarize discovered, usable, and rejected sources."""
        return {
            "discovered": len(sources),
            "usable": len(usable_sources),
            "rejected": len(sources) - len(usable_sources),
        }

    @staticmethod
    def _source_diagnostics(
        sources: list[dict[str, Any]],
        usable_sources: list[dict[str, Any]],
    ) -> list[dict[str, str]]:
        """Return concise diagnostics for sources that could not be used."""
        usable_urls = {source.get("url") for source in usable_sources}
        rejected = []

        for source in sources:
            if source.get("url") in usable_urls:
                continue

            error = source.get("error") or "No usable article text was extracted."
            rejected.append(
                {
                    "title": source.get("title", ""),
                    "url": source.get("url", ""),
                    "error": error,
                }
            )

        return rejected

    def run(
        self,
        question: str,
        max_results: int = 5,
    ) -> dict[str, Any]:
        """Run the research workflow with explicit evidence-quality safeguards."""
        question = question.strip()

        if not question:
            raise ValueError("Research question cannot be empty.")

        research_brief = self.researcher.research(question)

        sources = self._discover_sources(question, max_results)
        usable_sources = self._usable_sources(sources)
        source_summary = self._source_summary(sources, usable_sources)
        source_diagnostics = self._source_diagnostics(sources, usable_sources)

        if not sources:
            return {
                "question": question,
                "research_brief": research_brief,
                "status": "failed",
                "error": "No web research sources were found.",
                "sources": [],
                "ranked_sources": [],
                "best_sources": [],
                "source_summary": source_summary,
                "source_diagnostics": [],
                "evidence": {},
                "contradictions": {},
                "fact_checking": {},
                "analysis": {},
                "final_report": (
                    "# Research could not be completed\n\n"
                    "The search returned no sources. Please try again."
                ),
            }

        if not usable_sources:
            diagnostic_lines = [
                f"- [{item['title'] or item['url']}]({item['url']}): "
                f"{item['error']}"
                for item in source_diagnostics
            ]

            return {
                "question": question,
                "research_brief": research_brief,
                "status": "insufficient_sources",
                "error": (
                    "Search results were found, but no full article text "
                    "could be extracted. No evidence-based report was generated."
                ),
                "sources": sources,
                "ranked_sources": [],
                "best_sources": [],
                "source_summary": source_summary,
                "source_diagnostics": source_diagnostics,
                "evidence": {
                    "claims": [],
                    "summary": {
                        "total_claims": 0,
                        "message": "No usable article content was available.",
                    },
                },
                "contradictions": {
                    "summary": {
                        "message": (
                            "Contradiction analysis skipped because usable "
                            "article content was unavailable."
                        ),
                    },
                    "contradictions": [],
                },
                "fact_checking": {
                    "status": "not_performed",
                    "message": "No extracted claims were available to fact-check.",
                },
                "analysis": {
                    "status": "insufficient_sources",
                    "message": "Analysis requires accessible article content.",
                },
                "final_report": (
                    "# Research Report: Insufficient Source Evidence\n\n"
                    f"**Research question:** {question}\n\n"
                    "Search results were found, but the available pages did not "
                    "provide enough accessible article text to support a reliable "
                    "research report. Some sites may return access restrictions "
                    "or browser verification pages.\n\n"
                    "No substantive findings are presented because they could not "
                    "be grounded in extracted article content.\n\n"
                    "## Source access status\n\n"
                    + "\n".join(diagnostic_lines)
                    + "\n\nPlease retry later or use accessible full-text sources."
                ),
            }

        # Only validated, sufficiently long article text enters evidence analysis.
        ranked_sources = self.source_intelligence.rank_sources(
            usable_sources,
            question,
        )

        best_sources = self.source_intelligence.get_best_sources(
            ranked_sources,
            limit=3,
        )

        evidence = self.evidence_intelligence.analyze(
            ranked_sources,
            max_claims=10,
        )

        evidence_claims = evidence.get("claims", [])
        fact_check_claims = [
            claim.get("claim", "")
            for claim in evidence_claims
            if isinstance(claim, dict) and claim.get("claim")
        ]

        contradiction_claims = []
        for index, source in enumerate(ranked_sources, start=1):
            text = source.get("text", "").strip()
            if text:
                contradiction_claims.append(
                    {
                        "claim_id": f"source_claim_{index}",
                        "claim": text[:5000],
                        "source_domain": source.get("domain", ""),
                    }
                )

        contradiction_analysis = self.contradiction_detector.analyze(
            contradiction_claims
        )

        fact_checking = self.fact_checker.check_claims(
            fact_check_claims,
            ranked_sources,
        )

        analysis = self.analyst.analyze(
            question,
            ranked_sources,
        )

        synthesis = self.synthesizer.synthesize(
            question=question,
            sources=ranked_sources,
            fact_check=fact_checking,
            analysis=analysis,
            evidence=evidence,
            contradictions=contradiction_analysis,
            best_sources=best_sources,
        )

        return {
            "question": question,
            "research_brief": research_brief,
            "sources": sources,
            "ranked_sources": ranked_sources,
            "best_sources": best_sources,
            "source_summary": source_summary,
            "source_diagnostics": source_diagnostics,
            "evidence": evidence,
            "contradictions": contradiction_analysis,
            "fact_checking": fact_checking,
            "analysis": analysis,
            "final_report": synthesis,
            "status": "completed",
            "error": None,
        }
