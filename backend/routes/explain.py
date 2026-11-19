"""Beginner-friendly code explanation route."""

from fastapi import APIRouter, HTTPException
from backend.schemas.models import CodeRequest, ExplainResponse
from backend.services.explanation_service import explain_code

router = APIRouter(tags=["Explanation"])


@router.post("/explain", response_model=ExplainResponse)
async def explain_python_code(request: CodeRequest):
    """Generate plain-English explanations and analogies for Python code."""
    if not request.code or not request.code.strip():
        raise HTTPException(status_code=400, detail="Cannot explain empty code.")

    try:
        result = explain_code(
            code=request.code,
            override_key=request.api_key,
            override_model=request.model,
        )

        return ExplainResponse(
            success=result.get("success", False),
            has_syntax_warning=result.get("has_syntax_warning", False),
            syntax_warning_message=result.get("syntax_warning_message"),
            explanation=result.get("explanation", ""),
            error=result.get("error"),
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Explanation generation failed: {str(exc)}")
