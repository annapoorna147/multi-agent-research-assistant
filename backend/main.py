from fastapi import FastAPI

from backend.api.research import router as research_router


app = FastAPI(
    title="Multi-Agent Research Assistant V2",
    description="AI-powered multi-agent research platform",
    version="2.0.0",
)


app.include_router(research_router)


@app.get("/")
def root():
    return {
        "message": "Multi-Agent Research Assistant V2 API",
        "status": "online",
        "version": "2.0.0",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }