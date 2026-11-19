"""Documentation Service for CodeMate AI.

Automates generation of:
- Project README.md (description, features, installation, usage, inputs/outputs)
- Python code augmented with PEP 257 / Google-style docstrings
"""

from typing import Any, Dict, Optional

from backend.prompts.documentation_prompt import build_docstring_prompt, build_readme_prompt
from backend.services.gemini_service import gemini_service
from backend.services.validation_service import format_with_black, validate_syntax
from backend.utils.file_handler import extract_python_code


def generate_project_readme(
    code: str,
    override_key: Optional[str] = None,
    override_model: Optional[str] = None
) -> Dict[str, Any]:
    """Generate a comprehensive README.md for the provided Python codebase.

    Args:
        code: Python source code.
        override_key: Optional Gemini API key override.
        override_model: Optional Gemini model name override.

    Returns:
        Dict containing success status, markdown string, error.
    """
    if not code or not code.strip():
        return {
            "success": False,
            "error": "No Python code provided for documentation generation.",
            "readme_markdown": "",
        }

    system_instruction, user_prompt = build_readme_prompt(code)

    try:
        raw_output = gemini_service.generate_content(
            prompt=user_prompt,
            system_instruction=system_instruction,
            override_key=override_key,
            override_model=override_model,
        )

        # Clean markdown fences if the model wrapped the entire README in a code fence
        clean_readme = raw_output.strip()
        if clean_readme.startswith("```markdown"):
            clean_readme = clean_readme[11:].strip()
            if clean_readme.endswith("```"):
                clean_readme = clean_readme[:-3].strip()
        elif clean_readme.startswith("```md"):
            clean_readme = clean_readme[5:].strip()
            if clean_readme.endswith("```"):
                clean_readme = clean_readme[:-3].strip()

        return {
            "success": True,
            "readme_markdown": clean_readme,
            "error": None,
        }
    except Exception as exc:
        return {
            "success": False,
            "readme_markdown": "",
            "error": str(exc),
        }


def generate_code_docstrings(
    code: str,
    override_key: Optional[str] = None,
    override_model: Optional[str] = None
) -> Dict[str, Any]:
    """Generate Python source code enriched with Google-style docstrings and comments.

    Args:
        code: Python source code.
        override_key: Optional Gemini API key override.
        override_model: Optional Gemini model name override.

    Returns:
        Dict containing success status, documented_code, AST validation status.
    """
    if not code or not code.strip():
        return {
            "success": False,
            "error": "No code provided for docstring generation.",
            "documented_code": "",
        }

    system_instruction, user_prompt = build_docstring_prompt(code)

    try:
        raw_output = gemini_service.generate_content(
            prompt=user_prompt,
            system_instruction=system_instruction,
            override_key=override_key,
            override_model=override_model,
        )

        extracted_code = extract_python_code(raw_output)

        # Validate syntax of generated documented code
        val_res = validate_syntax(extracted_code)
        is_valid = val_res["valid"]

        final_code = extracted_code
        if is_valid:
            _, formatted, _ = format_with_black(extracted_code)
            final_code = formatted

        return {
            "success": True,
            "documented_code": final_code,
            "is_syntax_valid": is_valid,
            "syntax_error": val_res.get("error") if not is_valid else None,
            "error": None,
        }
    except Exception as exc:
        return {
            "success": False,
            "documented_code": "",
            "is_syntax_valid": False,
            "error": str(exc),
        }

