from tools.research_pipeline import ResearchPipeline


class OrchestratorAgent:
    """Agent responsible for coordinating the research workflow."""

    def __init__(self):
        self.pipeline = ResearchPipeline()

    def create_plan(self, question):
        """Create a simple research workflow plan."""

        return {
            "question": question,
            "steps": [
                "Create a research brief",
                "Search the web for relevant sources",
                "Extract readable source content",
                "Check important claims against source evidence",
                "Analyze findings across sources",
            ],
        }

    def run(self, question, max_results=5):
        """Run the research workflow."""

        plan = self.create_plan(question)

        result = self.pipeline.research(
            question,
            max_results=max_results,
        )

        return {
            "plan": plan,
            "sources": result["sources"],
            "fact_check": result["fact_check"],
            "analysis": result["analysis"],
        }