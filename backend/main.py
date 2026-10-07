from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.research import router as research_router


app = FastAPI(
    title="Multi-Agent Research Assistant V2",
    description="AI-powered multi-agent research platform",
    version="2.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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