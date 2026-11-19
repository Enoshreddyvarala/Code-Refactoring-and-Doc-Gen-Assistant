"""Prompt template for AI-powered Python code refactoring.

Provides structured prompts designed for beginner-friendly, clean,
PEP 8-compliant refactoring while preserving exact program functionality.
"""

from typing import List, Optional


SYSTEM_PROMPT = """You are a Senior Python Developer and patient programming mentor.
Your task is to refactor Python code submitted by developers and students.

Guiding Principles:
1. BEHAVIORAL PRESERVATION: Preserve the original program's functionality, inputs, outputs, and edge-case behavior.
2. PEP 8 COMPLIANCE: Use snake_case for functions and variables, PascalCase for classes, and UPPER_CASE for constants.
3. CLEAN CODE & READABILITY: Replace cryptic identifiers (e.g., x, tmp, data1) with descriptive names. Simplify deeply nested loops and conditionals.
4. TYPE ANNOTATIONS: Add clean, standard typing annotations (e.g., int, str, list[str], Optional) to improve clarity.
5. NO OVER-ENGINEERING: Keep solutions accessible to beginner and intermediate learners. Avoid unnecessary metaclasses, obscure lambdas, or complex third-party frameworks.
6. REMOVE CODE SMELLS: Fix mutable default arguments, bare 'except:' clauses, unused variables, and redundant logic.
7. CLEAR EDUCATIONAL EXPLANATIONS: Explain every major change so the student understands *why* the refactored version is superior.

Output Format Requirements:
- Start with the refactored code enclosed in a single ```python ... ``` markdown code block.
- Follow immediately with a structured explanation containing:
  - '### Refactoring Summary'
  - '### Key Improvements Made' (categorized into Naming, Structure, Safety, Style)
  - '### Beginner Tip / Takeaway'
"""


def build_refactoring_prompt(code: str, issues: Optional[List[str]] = None) -> tuple[str, str]:
    """Build system and user prompts for Python code refactoring.

    Args:
        code: The original Python source code.
        issues: Optional list of issues detected by static AST analysis.

    Returns:
        A tuple of (system_instruction, user_prompt).
    """
    user_prompt_parts = [
        "Please refactor the following Python code according to clean code and PEP 8 standards:\n",
        "```python",
        code.strip(),
        "```\n",
    ]

    if issues:
        user_prompt_parts.append("Static code analysis identified the following potential issues to address:")
        for issue in issues:
            user_prompt_parts.append(f"- {issue}")
        user_prompt_parts.append("")

    user_prompt_parts.append(
        "Please output the refactored code first in a ```python ... ``` block, "
        "followed by a clear, beginner-friendly explanation of all improvements."
    )

    return SYSTEM_PROMPT, "\n".join(user_prompt_parts)
