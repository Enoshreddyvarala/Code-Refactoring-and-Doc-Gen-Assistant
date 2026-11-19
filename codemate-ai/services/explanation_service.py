"""Code Explanation Service for CodeMate AI.

Generates beginner-friendly explanations of Python programs, including
real-world analogies, step-by-step execution flows, and function-by-function breakdowns.
"""

from typing import Any, Dict, Optional

from prompts.explanation_prompt import build_explanation_prompt
from services.gemini_service import gemini_service
from services.validation_service import validate_syntax


def explain_code(
    code: str,
    override_key: Optional[str] = None,
    override_model: Optional[str] = None
) -> Dict[str, Any]:
    """Generate comprehensive, beginner-friendly explanations for Python code.

    Args:
        code: Python source code string.
        override_key: Optional Gemini API key override.
        override_model: Optional Gemini model name override.

    Returns:
        Dict containing success status, explanation markdown, error details.
    """
    if not code or not code.strip():
        return {
            "success": False,
            "error": "No code provided for explanation.",
            "explanation": "",
        }

    # AST Syntax verification
    syntax_res = validate_syntax(code)
    has_syntax_error = not syntax_res["valid"]

    system_instruction, user_prompt = build_explanation_prompt(code)

    try:
        explanation_markdown = gemini_service.generate_content(
            prompt=user_prompt,
            system_instruction=system_instruction,
            override_key=override_key,
            override_model=override_model,
        )

        return {
            "success": True,
            "has_syntax_warning": has_syntax_error,
            "syntax_warning_message": syntax_res.get("error") if has_syntax_error else None,
            "explanation": explanation_markdown,
            "error": None,
        }
    except Exception as exc:
        return {
            "success": False,
            "has_syntax_warning": has_syntax_error,
            "explanation": "",
            "error": str(exc),
        }


def format_explanation_export(explanation: str, code: str) -> str:
    """Format explanation markdown into an exportable document.

    Args:
        explanation: Generated explanation markdown.
        code: Original Python source code.

    Returns:
        Complete Markdown document string.
    """
    return f"""# CodeMate AI — Python Code Explanation Report

## Analyzed Code
```python
{code.strip()}
```

---

{explanation}

---
*Report generated automatically by CodeMate AI — Developer Productivity & Learning Assistant.*
"""
