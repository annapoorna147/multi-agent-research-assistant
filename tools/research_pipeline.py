from tools.source_extractor import SourceExtractor
from tools.web_search import search_web


class ResearchPipeline:
    """Search for sources and extract their readable content."""

    def __init__(self):
        self.extractor = SourceExtractor()

    def research(self, query, max_results=5):
        """Search the web and extract content from the results."""

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

        return sources