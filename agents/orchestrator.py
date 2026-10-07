from tools.research_pipeline import ResearchPipeline


class OrchestratorAgent:
    """Thin orchestration wrapper for the V2 research pipeline."""

    def __init__(self):
        self.pipeline = ResearchPipeline()

    def create_plan(self, question):
        """Create a high-level research workflow plan."""

        return {
            "question": question,
            "steps": [
                "Create a research brief",
                "Search the web for relevant sources",
                "Extract readable source content",
                "Rank and evaluate source quality",
                "Map claims to supporting evidence",
                "Detect contradictions and uncertainties",
                "Fact-check important claims",
                "Analyze findings across sources",
                "Synthesize the final research report",
            ],
        }

    def run(self, question, max_results=5):
        """Run the complete V2 research workflow."""

        plan = self.create_plan(question)

        result = self.pipeline.run(
            question,
            max_results=max_results,
        )

        return {
            "plan": plan,
            "status": result.get("status"),
            "question": result.get("question"),
            "research_brief": result.get(
                "research_brief"
            ),
            "sources": result.get(
                "sources",
                [],
            ),
            "ranked_sources": result.get(
                "ranked_sources",
                [],
            ),
            "best_sources": result.get(
                "best_sources",
                [],
            ),
            "evidence": result.get(
                "evidence",
                {},
            ),
            "contradictions": result.get(
                "contradictions",
                {},
            ),
            "fact_checking": result.get(
                "fact_checking",
                {},
            ),
            "analysis": result.get(
                "analysis",
                {},
            ),
            "final_report": result.get(
                "final_report",
                "",
            ),
        }