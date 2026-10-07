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
    """
    V2 end-to-end research orchestration.

    Flow:

        Question
            ↓
        Research Planning
            ↓
        Web Search
            ↓
        Source Extraction
            ↓
        Source Intelligence
            ↓
        Source Ranking
            ↓
        Best Sources
            ↓
        Evidence Intelligence
            ↓
        Contradiction Detection
            ↓
        Fact Checking
            ↓
        Analysis
            ↓
        AI Synthesis
            ↓
        Final Research Report
    """

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
        """
        Search the web and enrich search results with
        extracted page content.
        """

        search_results = search_web(
            question,
            max_results=max_results,
        )

        enriched_sources = []

        for result in search_results:
            url = result.get("url", "")

            if not url:
                continue

            extracted = self.source_extractor.extract(url)

            source = {
                "title": result.get("title", ""),
                "url": url,
                "snippet": result.get("snippet", ""),
                "text": extracted.get("text", ""),
                "success": extracted.get("success", False),
                "error": extracted.get("error", ""),
            }

            enriched_sources.append(source)

        return enriched_sources

    def run(
        self,
        question: str,
        max_results: int = 5,
    ) -> dict[str, Any]:
        """
        Run the complete V2 research workflow.
        """

        question = question.strip()

        if not question:
            raise ValueError(
                "Research question cannot be empty."
            )

        # --------------------------------------------------
        # 1. Research planning
        # --------------------------------------------------

        research_brief = self.researcher.research(
            question
        )

        # --------------------------------------------------
        # 2. Web search + source extraction
        # --------------------------------------------------

        sources = self._discover_sources(
            question,
            max_results,
        )

        if not sources:
            return {
                "question": question,
                "research_brief": research_brief,
                "status": "failed",
                "error": "No web research sources were found.",
            }

        # --------------------------------------------------
        # 3. Source intelligence + ranking
        # --------------------------------------------------

        ranked_sources = self.source_intelligence.rank_sources(
            sources,
            question,
        )

        best_sources = self.source_intelligence.get_best_sources(
            ranked_sources,
            limit=3,
        )

        # --------------------------------------------------
        # 4. Evidence intelligence
        # --------------------------------------------------

        evidence = self.evidence_intelligence.analyze(
            ranked_sources,
            max_claims=10,
        )

        # --------------------------------------------------
        # 5. Contradiction detection
        # --------------------------------------------------

        contradiction_claims = []

        for index, source in enumerate(ranked_sources):
            text = source.get("text", "")

            if not text:
                text = source.get("snippet", "")

            if not text:
                continue

            contradiction_claims.append(
                {
                    "claim_id": f"source_claim_{index + 1}",
                    "claim": text[:5000],
                    "source_domain": source.get(
                        "domain",
                        "",
                    ),
                }
            )

        contradiction_analysis = (
            self.contradiction_detector.analyze(
                contradiction_claims
            )
        )

        # --------------------------------------------------
        # 6. Fact checking
        # --------------------------------------------------

        fact_checking = self.fact_checker.check_claims(
            [],
            ranked_sources,
        )

        # --------------------------------------------------
        # 7. Analysis
        # --------------------------------------------------

        analysis = self.analyst.analyze(
            question,
            ranked_sources,
        )

        # --------------------------------------------------
        # 8. AI synthesis
        # --------------------------------------------------

        synthesis = self.synthesizer.synthesize(
            question=question,
            sources=ranked_sources,
            fact_check=fact_checking,
            analysis=analysis,
            evidence=evidence,
            contradictions=contradiction_analysis,
            best_sources=best_sources,
        )

        # --------------------------------------------------
        # 9. Final structured result
        # --------------------------------------------------

        return {
            "question": question,
            "research_brief": research_brief,
            "sources": sources,
            "ranked_sources": ranked_sources,
            "best_sources": best_sources,
            "evidence": evidence,
            "contradictions": contradiction_analysis,
            "fact_checking": fact_checking,
            "analysis": analysis,
            "final_report": synthesis,
            "status": "completed",
        }