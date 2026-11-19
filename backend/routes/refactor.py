"""AI-powered code refactoring route."""

from fastapi import APIRouter, HTTPException
from backend.schemas.models import CodeRequest, RefactorResponse
from backend.services.refactoring_service import refactor_code

router = APIRouter(tags=["Refactoring"])


@router.post("/refactor", response_model=RefactorResponse)
async def refactor_python_code(request: CodeRequest):
    """Refactor Python code preserving functionality using Google Gemini."""
    if not request.code or not request.code.strip():
        raise HTTPException(status_code=400, detail="Cannot refactor empty code.")

    try:
        result = refactor_code(
            code=request.code,
            override_key=request.api_key,
            override_model=request.model,
        )

        return RefactorResponse(
            success=result.get("success", False),
            is_syntax_valid=result.get("is_syntax_valid", False),
            syntax_error=result.get("syntax_error"),
            original_code=result.get("original_code", request.code),
            refactored_code=result.get("refactored_code", ""),
            explanation=result.get("explanation", ""),
            diff=result.get("diff", ""),
            original_analysis=result.get("original_analysis", {}),
            refactored_analysis=result.get("refactored_analysis", {}),
            health_score_delta=result.get("health_score_delta", 0),
            error=result.get("error"),
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Refactoring process failed: {str(exc)}")
