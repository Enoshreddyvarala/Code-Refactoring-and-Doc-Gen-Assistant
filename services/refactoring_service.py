"""Refactoring Service for CodeMate AI.

Orchestrates Gemini AI-powered refactoring, performs AST pre- and post-validation,
runs Black formatting, computes metrics delta, and extracts structured explanations.
"""

from typing import Any, Dict, Optional

from prompts.refactoring_prompt import build_refactoring_prompt
from services.code_analyzer import analyze_code
from services.gemini_service import gemini_service
from services.validation_service import format_with_black, validate_syntax
from utils.file_handler import extract_python_code, generate_diff


def refactor_code(
    code: str,
    override_key: Optional[str] = None,
    override_model: Optional[str] = None
) -> Dict[str, Any]:
    """Execute AI-powered refactoring on Python source code.

    Args:
        code: The original Python source code.
        override_key: Optional Gemini API key override.
        override_model: Optional Gemini model name override.

    Returns:
        Dictionary containing:
        - success: bool
        - original_code: str
        - refactored_code: str
        - explanation: str
        - diff: str
        - original_metrics: dict
        - refactored_metrics: dict
        - error: Optional[str]
    """
    if not code or not code.strip():
        return {
            "success": False,
            "error": "No Python code provided for refactoring.",
            "original_code": code,
            "refactored_code": "",
            "explanation": "",
            "diff": "",
            "original_metrics": {},
            "refactored_metrics": {},
        }

    # 1. Analyze original code first
    original_analysis = analyze_code(code)
    issue_descriptions = [f"{iss['title']} (Line {iss.get('line', '?')}): {iss['description']}" for iss in original_analysis.get("issues", [])]

    # 2. Build prompt with detected issues for targeted refactoring
    system_instruction, user_prompt = build_refactoring_prompt(code, issue_descriptions)

    # 3. Call Gemini
    try:
        raw_response = gemini_service.generate_content(
            prompt=user_prompt,
            system_instruction=system_instruction,
            override_key=override_key,
            override_model=override_model,
        )
    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
            "original_code": code,
            "refactored_code": "",
            "explanation": "",
            "diff": "",
            "original_metrics": original_analysis.get("metrics", {}),
            "refactored_metrics": {},
        }

    # 4. Extract refactored code and explanation
    extracted_code = extract_python_code(raw_response)

    # Separate explanation text (remove the python code block if present)
    explanation_text = raw_response
    if "```python" in explanation_text:
        parts = explanation_text.split("```")
        # Text after the code block
        after_code_parts = [p for i, p in enumerate(parts) if i >= 2 and not p.startswith("python")]
        explanation_text = "\n".join(after_code_parts).strip()
    elif "```" in explanation_text:
        parts = explanation_text.split("```")
        after_code_parts = [p for i, p in enumerate(parts) if i >= 2]
        explanation_text = "\n".join(after_code_parts).strip()

    if not explanation_text.strip():
        explanation_text = "Code successfully refactored according to clean code standards and PEP 8 conventions."

    # 5. Validate refactored code with AST
    syntax_check = validate_syntax(extracted_code)
    is_valid = syntax_check["valid"]

    # 6. Apply Black formatting to refactored code if valid
    final_code = extracted_code
    if is_valid:
        _, formatted, _ = format_with_black(extracted_code)
        final_code = formatted

    # 7. Post-refactoring analysis for metrics comparison
    refactored_analysis = analyze_code(final_code)

    # 8. Compute unified diff
    diff_output = generate_diff(code, final_code)

    return {
        "success": True,
        "is_syntax_valid": is_valid,
        "syntax_error": syntax_check.get("error") if not is_valid else None,
        "original_code": code,
        "refactored_code": final_code,
        "explanation": explanation_text,
        "diff": diff_output,
        "original_analysis": original_analysis,
        "refactored_analysis": refactored_analysis,
        "health_score_delta": refactored_analysis.get("health_score", 100) - original_analysis.get("health_score", 0),
        "error": None,
    }
