"""CodeMate AI — FastAPI Backend Application.

Provides RESTful API endpoints for:
- Python AST Code Analysis & Health Scoring
- AI Refactoring & Explanation (Google Gemini)
- Automated README & Docstring Generation
- Black Formatting & Sandboxed Subprocess Test Execution
"""

import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Load local environment variables from workspace root
load_dotenv(override=True)

from backend.routes import (
    analyze,
    document,
    explain,
    health,
    refactor,
    samples,
    validate,
)

app = FastAPI(
    title="CodeMate AI Backend API",
    description="REST API for CodeMate AI - Code Refactoring & Documentation Assistant",
    version="2.0.0",
)

# Enable CORS for React frontend (Vite default is 5173, also permit local variations)
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {str(exc)}"},
    )

# Include API Routers with /api prefix
app.include_router(health.router, prefix="/api")
app.include_router(analyze.router, prefix="/api")
app.include_router(refactor.router, prefix="/api")
app.include_router(explain.router, prefix="/api")
app.include_router(document.router, prefix="/api")
app.include_router(validate.router, prefix="/api")
app.include_router(samples.router, prefix="/api")


@app.get("/")
async def root():
    """Root status endpoint."""
    return {
        "app": "CodeMate AI API",
        "version": "2.0.0",
        "status": "online",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
