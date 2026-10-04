from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from agents.orchestrator import OrchestratorAgent


router = APIRouter(
    prefix="/api/research",
    tags=["Research"],
)


class ResearchRequest(BaseModel):
    question: str
    mode: Literal["Quick", "Standard", "Deep"] = "Standard"


class ResearchResponse(BaseModel):
    question: str
    mode: str
    status: str
    result: dict


def get_max_results(mode: str) -> int:
    if mode == "Quick":
        return 3

    if mode == "Deep":
        return 8

    return 5


@router.post("/", response_model=ResearchResponse)
def start_research(request: ResearchRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Research question cannot be empty.",
        )

    max_results = get_max_results(request.mode)

    try:
        orchestrator = OrchestratorAgent()

        result = orchestrator.run(
            question,
            max_results=max_results,
        )

        return ResearchResponse(
            question=question,
            mode=request.mode,
            status="completed",
            result=result,
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Research failed: {str(error)}",
        ) from error