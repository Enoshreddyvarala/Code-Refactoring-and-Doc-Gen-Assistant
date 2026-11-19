"""Validation, Black formatting, and isolated test execution route."""

from fastapi import APIRouter, HTTPException
from backend.schemas.models import ValidationRequest, ValidationResponse
from backend.services.validation_service import (
    format_with_black,
    run_isolated_test_suite,
    validate_syntax,
)

router = APIRouter(tags=["Validation"])


@router.post("/validate", response_model=ValidationResponse)
async def validate_or_test_code(request: ValidationRequest):
    """Validate syntax, format with Black, or run tests in an isolated sandbox."""
    if not request.code or not request.code.strip():
        raise HTTPException(status_code=400, detail="Cannot validate empty code.")

    action = request.action.lower()

    if action == "format_black":
        ok, formatted, msg = format_with_black(request.code)
        syntax_res = validate_syntax(formatted)
        return ValidationResponse(
            syntax_valid=syntax_res["valid"],
            formatted_code=formatted,
            black_message=msg,
            error=syntax_res.get("error"),
            line=syntax_res.get("line"),
            column=syntax_res.get("column"),
            symbols=syntax_res.get("symbols"),
        )

    elif action == "run_tests":
        if not request.test_code or not request.test_code.strip():
            raise HTTPException(status_code=400, detail="Test code / assertions required for test execution.")
        test_res = run_isolated_test_suite(request.code, request.test_code)
        return ValidationResponse(
            syntax_valid=test_res.get("passed", False),
            test_result=test_res,
            error=test_res.get("error"),
        )

    else:
        # Default action: static syntax validation
        val_res = validate_syntax(request.code)
        return ValidationResponse(
            syntax_valid=val_res["valid"],
            error=val_res.get("error"),
            line=val_res.get("line"),
            column=val_res.get("column"),
            symbols=val_res.get("symbols"),
        )
