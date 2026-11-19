"""Automated README and docstring documentation route."""

from fastapi import APIRouter, HTTPException
from backend.schemas.models import DocRequest, DocResponse
from backend.services.documentation_service import (
    generate_code_docstrings,
    generate_project_readme,
)

router = APIRouter(tags=["Documentation"])


@router.post("/document", response_model=DocResponse)
async def document_python_code(request: DocRequest):
    """Generate Markdown README and/or Google-style docstrings."""
    if not request.code or not request.code.strip():
        raise HTTPException(status_code=400, detail="Cannot document empty code.")

    readme_markdown = None
    documented_code = None
    is_syntax_valid = None
    error_messages = []

    try:
        # Generate README if requested
        if request.doc_type in ("readme", "all"):
            readme_res = generate_project_readme(
                code=request.code,
                override_key=request.api_key,
                override_model=request.model,
            )
            if readme_res.get("success"):
                readme_markdown = readme_res.get("readme_markdown")
            else:
                error_messages.append(f"README generation error: {readme_res.get('error')}")

        # Generate Docstrings if requested
        if request.doc_type in ("docstrings", "all"):
            doc_res = generate_code_docstrings(
                code=request.code,
                override_key=request.api_key,
                override_model=request.model,
            )
            if doc_res.get("success"):
                documented_code = doc_res.get("documented_code")
                is_syntax_valid = doc_res.get("is_syntax_valid")
            else:
                error_messages.append(f"Docstring generation error: {doc_res.get('error')}")

        success = (readme_markdown is not None) or (documented_code is not None)
        err = "; ".join(error_messages) if error_messages else None

        return DocResponse(
            success=success,
            readme_markdown=readme_markdown,
            documented_code=documented_code,
            is_syntax_valid=is_syntax_valid,
            error=err,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Documentation generation failed: {str(exc)}")
