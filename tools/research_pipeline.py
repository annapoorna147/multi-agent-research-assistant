from typing import Any

from agents.analyst import AnalystAgent
from agents.fact_checker import FactCheckerAgent
from agents.researcher import ResearcherAgent
from agents.synthesizer import SynthesizerAgent
from tools.contradiction_detector import ContradictionDetector
from tools.evidence_intelligence import EvidenceIntelligence
from tools.source_intelligence import SourceIntelligence


class ResearchPipeline:
    """
    V2 end-to-end research pipeline.

    Flow:

        Question
            ↓
        Research / Search
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
        Synthesis
            ↓
        Final Research Report
    """

    def __init__(self) -> None:
        self.researcher = ResearcherAgent()
        self.source_intelligence = SourceIntelligence()
        self.evidence_intelligence = EvidenceIntelligence()
        self.contradiction_detector = ContradictionDetector()
        self.fact_checker = FactCheckerAgent()
        self.analyst = AnalystAgent()
        self.synthesizer = SynthesizerAgent()

    def run(
        self,
        question: str,
        max_results: int = 5,
    ) -> dict[str, Any]:
        """
        Run the complete research pipeline.
        """

        question = question.strip()

        if not question:
            raise ValueError("Research question cannot be empty.")

        # ------------------------------------------------------------------
        # 1. Research / Search
        # ------------------------------------------------------------------

        research_result = self.researcher.research(
            question,
            max_results=max_results,
        )

        # Researcher may return either a list directly or a dictionary.
        if isinstance(research_result, dict):
            sources = research_result.get(
                "sources",
                research_result.get("results", []),
            )
        else:
            sources = research_result

        if not sources:
            return {
                "question": question,
                "status": "failed",
                "error": "No research sources were found.",
            }

        # ------------------------------------------------------------------
        # 2. Source Intelligence
        # ------------------------------------------------------------------

        source_analysis = self.source_intelligence.analyze_sources(
            sources,
            question,
        )

        # Support both possible return structures.
        if isinstance(source_analysis, dict):
            ranked_sources = source_analysis.get(
                "ranked_sources",
                source_analysis.get("sources", []),
            )
        else:
            ranked_sources = source_analysis

        # ------------------------------------------------------------------
        # 3. Best Sources
        # ------------------------------------------------------------------

        best_sources = self.source_intelligence.get_best_sources(
            ranked_sources,
            limit=3,
        )

        # ------------------------------------------------------------------
        # 4. Evidence Intelligence
        # ------------------------------------------------------------------

        evidence = self.evidence_intelligence.analyze(
            ranked_sources,
            max_claims=10,
        )

        # ------------------------------------------------------------------
        # 5. Contradiction Detection
        # ------------------------------------------------------------------
        #
        # We intentionally build contradiction claims from source snippets.
        #
        # EvidenceIntelligence may extract only one formal claim from a group
        # of sources. That would prevent the contradiction detector from
        # comparing different sources.
        #
        # Source-level comparison allows Research AI to detect disagreements
        # even when the evidence extractor does not convert every source into
        # a formal claim.
        # ------------------------------------------------------------------

        contradiction_claims = []

        for index, source in enumerate(ranked_sources):
            snippet = source.get("snippet", "")
            domain = source.get("domain", "")

            if not snippet:
                snippet = source.get("text", "")

            if not snippet:
                continue

            contradiction_claims.append(
                {
                    "claim_id": f"source_claim_{index + 1}",
                    "claim": snippet,
                    "source_domain": domain,
                }
            )

        contradiction_analysis = (
            self.contradiction_detector.analyze(
                contradiction_claims
            )
        )

        # ------------------------------------------------------------------
        # 6. Fact Checking
        # ------------------------------------------------------------------

        fact_checking = self.fact_checker.check(
            question,
            ranked_sources,
        )

        # ------------------------------------------------------------------
        # 7. Cross-source Analysis
        # ------------------------------------------------------------------

        analysis = self.analyst.analyze(
            question,
            ranked_sources,
        )

        # ------------------------------------------------------------------
        # 8. Final Synthesis
        # ------------------------------------------------------------------

        synthesis = self.synthesizer.synthesize(
            question,
            ranked_sources,
            fact_checking,
            analysis,
        )

        # ------------------------------------------------------------------
        # 9. Final Result
        # ------------------------------------------------------------------

        return {
            "question": question,
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