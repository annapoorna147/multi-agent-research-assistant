from ddgs import DDGS


class WebSearchTool:
    """Tool for searching the web."""

    def __init__(self):
        self.search_engine = DDGS()

    def search(self, query, max_results=5):
        """Search the web and return structured results."""

        results = self.search_engine.text(
            query,
            max_results=max_results,
        )

        return [
            {
                "title": result.get("title", ""),
                "url": result.get("href", ""),
                "snippet": result.get("body", ""),
            }
            for result in results
        ]


def search_web(query, max_results=5):
    """Convenience function for web searches."""

    tool = WebSearchTool()
    return tool.search(query, max_results)