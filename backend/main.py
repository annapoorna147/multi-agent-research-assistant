
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.research import router as research_router


app = FastAPI(
    title="Multi-Agent Research Assistant V2",
    description="AI-powered multi-agent research platform",
    version="2.0.0",
)


allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

frontend_origin = os.getenv("FRONTEND_ORIGIN", "").strip().rstrip("/")

if frontend_origin:
    allowed_origins.append(frontend_origin)


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
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
