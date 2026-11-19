"""Code analysis route using Python AST and Black."""

from fastapi import APIRouter, HTTPException
from backend.schemas.models import AnalysisResponse, CodeRequest
from backend.services.code_analyzer import analyze_code

router = APIRouter(tags=["Analysis"])


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_python_code(request: CodeRequest):
    """Analyze Python code using AST and Black formatting checks."""
    if not request.code or not request.code.strip():
        raise HTTPException(status_code=400, detail="Cannot analyze empty code.")

    try:
        result = analyze_code(request.code)
        return AnalysisResponse(
            syntax_valid=result.get("syntax_valid", False),
            health_score=result.get("health_score", 0),
            metrics=result.get("metrics", {}),
            issues=result.get("issues", []),
            black_compliant=result.get("black_compliant", False),
            black_message=result.get("black_message", ""),
            disclaimer=result.get("disclaimer", ""),
            error=result.get("error"),
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Code analysis failed: {str(exc)}")
