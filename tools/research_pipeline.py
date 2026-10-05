from agents.analyst import AnalystAgent
from agents.fact_checker import FactCheckerAgent
from tools.source_extractor import SourceExtractor
from tools.source_intelligence import SourceIntelligence
from tools.web_search import search_web


class ResearchPipeline:
    """Search, evaluate, rank, fact-check, and analyze research sources."""

    def __init__(self):
        self.extractor = SourceExtractor()
        self.fact_checker = FactCheckerAgent()
        self.analyst = AnalystAgent()
        self.source_intelligence = SourceIntelligence()

    def research(self, query, max_results=5):
        """Run the complete research pipeline."""

        # ---------------------------------------------------------
        # STEP 1: Search the web
        # ---------------------------------------------------------

        search_results = search_web(
            query,
            max_results,
        )

        # ---------------------------------------------------------
        # STEP 2: Extract source content
        # ---------------------------------------------------------

        sources = []

        for result in search_results:
            extracted = self.extractor.extract(
                result["url"]
            )

            sources.append(
                {
                    "title": result["title"],
                    "url": result["url"],
                    "snippet": result["snippet"],
                    "text": extracted["text"],
                    "success": extracted["success"],
                }
            )

        # ---------------------------------------------------------
        # STEP 3: Source Intelligence
        # ---------------------------------------------------------

        ranked_sources = (
            self.source_intelligence.rank_sources(
                sources,
                query,
            )
        )

        # ---------------------------------------------------------
        # STEP 4: Identify the best accessible sources
        # ---------------------------------------------------------

        best_sources = (
            self.source_intelligence.get_best_sources(
                ranked_sources,
                limit=3,
            )
        )

        # ---------------------------------------------------------
        # STEP 5: Prepare claims for fact checking
        # ---------------------------------------------------------

        claims = [
            source["snippet"]
            for source in ranked_sources
            if source.get("snippet")
        ]

        # ---------------------------------------------------------
        # STEP 6: Fact checking
        # ---------------------------------------------------------

        fact_check = self.fact_checker.check_claims(
            claims,
            ranked_sources,
        )

        # ---------------------------------------------------------
        # STEP 7: Analysis
        # ---------------------------------------------------------

        analysis = self.analyst.analyze(
            query,
            ranked_sources,
        )

        # ---------------------------------------------------------
        # STEP 8: Return enriched research result
        # ---------------------------------------------------------

        return {
            "query": query,
            "research_intent": (
                self.source_intelligence.detect_research_intent(
                    query
                )
            ),
            "sources": ranked_sources,
            "best_sources": best_sources,
            "fact_check": fact_check,
            "analysis": analysis,
        }