"""File handling and text utilities for CodeMate AI.

Includes functions for reading uploaded files, generating formatted diffs,
extracting clean Python code from LLM responses, and building exportable reports.
"""

import difflib
import re
from typing import Optional, Tuple


def read_uploaded_file(uploaded_file) -> Tuple[bool, str, str]:
    """Safely read and decode an uploaded Streamlit file.

    Args:
        uploaded_file: Streamlit UploadedFile object.

    Returns:
        Tuple of (success, content_string, error_message).
    """
    if uploaded_file is None:
        return False, "", "No file uploaded."

    try:
        raw_bytes = uploaded_file.getvalue()
        # Attempt UTF-8 first, fallback to latin-1
        try:
            content = raw_bytes.decode("utf-8")
        except UnicodeDecodeError:
            content = raw_bytes.decode("latin-1")
        return True, content, ""
    except Exception as exc:
        return False, "", f"Failed to read file: {str(exc)}"


def extract_python_code(llm_output: str) -> str:
    """Extract clean Python code from LLM response containing markdown code blocks.

    Handles:
    - ```python ... ```
    - ``` ... ```
    - Plain raw code if no markdown fences are present.

    Args:
        llm_output: The raw text response from the Gemini model.

    Returns:
        Extracted and trimmed Python code string.
    """
    if not llm_output or not llm_output.strip():
        return ""

    # Look for ```python ... ``` block first
    python_block_match = re.search(r"```(?:python|py)\s*\n(.*?)```", llm_output, re.DOTALL | re.IGNORECASE)
    if python_block_match:
        return python_block_match.group(1).strip()

    # Look for generic ``` ... ``` block
    generic_block_match = re.search(r"```\s*\n(.*?)```", llm_output, re.DOTALL)
    if generic_block_match:
        return generic_block_match.group(1).strip()

    # If no fences, check if the text looks like raw Python (e.g., starts with def, import, class)
    lines = llm_output.strip().splitlines()
    code_lines = []
    in_code = False
    for line in lines:
        if line.strip().startswith(("import ", "from ", "def ", "class ", "#", "if ", "for ", "while ")):
            in_code = True
        if in_code:
            code_lines.append(line)

    if code_lines:
        return "\n".join(code_lines).strip()

    return llm_output.strip()


def generate_diff(original_code: str, refactored_code: str, fromfile: str = "Original", tofile: str = "Refactored") -> str:
    """Generate a clean unified diff between original and refactored code.

    Args:
        original_code: Original Python source code.
        refactored_code: Refactored Python source code.
        fromfile: Label for original code.
        tofile: Label for refactored code.

    Returns:
        Unified diff string.
    """
    orig_lines = original_code.splitlines(keepends=True)
    refact_lines = refactored_code.splitlines(keepends=True)

    diff = difflib.unified_diff(
        orig_lines,
        refact_lines,
        fromfile=fromfile,
        tofile=tofile,
        n=3
    )
    return "".join(diff)


def create_analysis_export_markdown(analysis_results: dict, code: str) -> str:
    """Format AST code analysis results into a clean, downloadable Markdown report.

    Args:
        analysis_results: Dictionary containing AST issues and metrics.
        code: Source code analyzed.

    Returns:
        Formatted Markdown report string.
    """
    metrics = analysis_results.get("metrics", {})
    health = analysis_results.get("health_score", 100)
    issues = analysis_results.get("issues", [])
    black_check = analysis_results.get("black_compliant", False)

    lines = [
        "# CodeMate AI — Code Analysis Report",
        "",
        f"**Overall Health Score:** {health}/100",
        f"**PEP 8 / Black Compliant:** {'Yes' if black_check else 'No'}",
        "",
        "## Summary Metrics",
        f"- **Total Lines of Code (LOC):** {metrics.get('loc', 0)}",
        f"- **Logical Code Lines:** {metrics.get('code_lines', 0)}",
        f"- **Comments:** {metrics.get('comment_lines', 0)}",
        f"- **Blank Lines:** {metrics.get('blank_lines', 0)}",
        f"- **Functions:** {metrics.get('functions_count', 0)}",
        f"- **Classes:** {metrics.get('classes_count', 0)}",
        f"- **Imports:** {metrics.get('imports_count', 0)}",
        f"- **Cyclomatic Complexity (Estimate):** {metrics.get('cyclomatic_complexity', 1)}",
        "",
        "## Detected Issues & Observations",
    ]

    if not issues:
        lines.append("No critical issues or anti-patterns detected. Code is clean and well-structured!")
    else:
        for idx, issue in enumerate(issues, start=1):
            severity = issue.get("severity", "Info").upper()
            title = issue.get("title", "")
            desc = issue.get("description", "")
            line_no = issue.get("line", None)
            loc_str = f" (Line {line_no})" if line_no else ""
            lines.append(f"### {idx}. [{severity}] {title}{loc_str}")
            lines.append(f"{desc}")
            if issue.get("suggestion"):
                lines.append(f"*Recommendation:* {issue['suggestion']}")
            lines.append("")

    lines.extend([
        "## Analyzed Source Code",
        "```python",
        code.strip(),
        "```",
        "",
        "---",
        "*Report generated automatically by CodeMate AI — Developer Productivity & Learning Assistant.*"
    ])

    return "\n".join(lines)
