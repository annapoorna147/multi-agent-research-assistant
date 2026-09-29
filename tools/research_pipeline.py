from agents.analyst import AnalystAgent
from tools.source_extractor import SourceExtractor
from tools.web_search import search_web


class ResearchPipeline:
    """Search for sources, extract content, and analyze findings."""

    def __init__(self):
        self.extractor = SourceExtractor()
        self.analyst = AnalystAgent()

    def research(self, query, max_results=5):
        """Search, extract, and analyze research sources."""

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

        analysis = self.analyst.analyze(sources)

        return {
            "query": query,
            "sources": sources,
            "analysis": analysis,
        }