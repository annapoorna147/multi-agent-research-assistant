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


def get_error_status(error: Exception) -> int:
    """
    Convert known temporary/external service errors
    into an appropriate HTTP status.
    """

    message = str(error).lower()

    if (
        "503" in message
        or "unavailable" in message
        or "high demand" in message
    ):
        return 503

    if (
        "429" in message
        or "resource exhausted" in message
        or "rate limit" in message
    ):
        return 429

    if (
        "timeout" in message
        or "timed out" in message
    ):
        return 504

    return 500


@router.post(
    "/",
    response_model=ResearchResponse,
)
def start_research(
    request: ResearchRequest,
):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Research question cannot be empty.",
        )

    max_results = get_max_results(
        request.mode
    )

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
        status_code = get_error_status(error)

        if status_code == 503:
            detail = (
                "The AI research service is temporarily "
                "unavailable due to high demand. "
                "Please try again shortly."
            )

        elif status_code == 429:
            detail = (
                "The AI research service is temporarily "
                "rate-limited. Please try again shortly."
            )

        elif status_code == 504:
            detail = (
                "The research request timed out. "
                "Please try again."
            )

        else:
            detail = (
                f"Research failed: {str(error)}"
            )

        raise HTTPException(
            status_code=status_code,
            detail=detail,
        ) from error