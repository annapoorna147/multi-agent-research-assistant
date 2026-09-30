from agents.analyst import AnalystAgent
from agents.fact_checker import FactCheckerAgent
from tools.source_extractor import SourceExtractor
from tools.web_search import search_web


class ResearchPipeline:
    """Search, extract, fact-check, and analyze research sources."""

    def __init__(self):
        self.extractor = SourceExtractor()
        self.fact_checker = FactCheckerAgent()
        self.analyst = AnalystAgent()

    def research(self, query, max_results=5):
        """Run the complete research pipeline."""

        search_results = search_web(query, max_results)

        sources = []

        for result in search_results:
            extracted = self.extractor.extract(result["url"])

            sources.append(
                {
                    "title": result["title"],
                    "url": result["url"],
                    "snippet": result["snippet"],
                    "text": extracted["text"],
                    "success": extracted["success"],
                }
            )

        claims = [
            source["snippet"]
            for source in sources
            if source.get("snippet")
        ]

        fact_check = self.fact_checker.check_claims(
            claims,
            sources,
        )

        analysis = self.analyst.analyze(sources)

        return {
            "query": query,
            "sources": sources,
            "fact_check": fact_check,
            "analysis": analysis,
        }