"""Prompt templates for AI-powered Python documentation generation.

Supports generating comprehensive Markdown README files and
PEP 257 / Google-style docstrings for Python codebases.
"""


README_SYSTEM_PROMPT = """You are a Technical Writer and Senior Software Engineer.
Your task is to generate a comprehensive, professional, beginner-friendly README.md for a Python project.

The generated README.md must strictly adhere to the following structure:
# Project Title
A clear, catchy title reflecting the program's purpose.

## Description
A concise yet comprehensive explanation of what the program does and why it is useful.

## Key Features
A bulleted list highlighting key capabilities.

## Architecture & How It Works
Briefly describe the components, flow, and design logic.

## Prerequisites & Dependencies
List Python version requirements and any required standard library or external packages.

## Installation & Setup
Step-by-step commands to set up the project locally.

## Usage Guide
How to run the script or import its functions, with example CLI commands.

## Example Inputs & Outputs
Provide realistic code examples with expected outputs (sample inputs, return values, or console outputs).

## Function Reference
A summary table or list of the functions/classes, their arguments, and their return values.

## License
Mention MIT License or open educational use.

Write standard, clean GitHub-flavored markdown. Do not wrap the whole response in a markdown code block—return the raw markdown directly.
"""


DOCSTRING_SYSTEM_PROMPT = """You are a Senior Python Engineer focused on code clarity and documentation standards.
Your task is to take the provided Python code and return the exact same code with complete, professional docstrings added according to PEP 257 and Google docstring style.

Requirements:
1. Add a module-level docstring at the top.
2. Add detailed docstrings for every class, method, and function.
3. Include Args, Returns, and Raises sections where applicable.
4. Add clear inline comments explaining non-trivial logic for beginners.
5. PRESERVE ALL ORIGINAL CODE LOGIC AND FUNCTIONALITY EXACTLY.
6. Output ONLY the complete Python code wrapped in a single ```python ... ``` markdown block.
"""


def build_readme_prompt(code: str) -> tuple[str, str]:
    """Build prompts for generating a project README.md.

    Args:
        code: Python source code of the project.

    Returns:
        A tuple of (system_instruction, user_prompt).
    """
    user_prompt = f"""Generate a complete, professional, and beginner-friendly README.md file based on the following Python source code:

```python
{code.strip()}
```

Follow all standard sections including Overview, Features, Prerequisites, Installation, Usage, and Example Inputs & Outputs."""

    return README_SYSTEM_PROMPT, user_prompt


def build_docstring_prompt(code: str) -> tuple[str, str]:
    """Build prompts for adding comprehensive docstrings to Python code.

    Args:
        code: Python source code.

    Returns:
        A tuple of (system_instruction, user_prompt).
    """
    user_prompt = f"""Please add comprehensive Google-style docstrings and beginner-friendly comments to every function and class in the following Python code without altering its behavior:

```python
{code.strip()}
```

Return the complete Python code in a single ```python ... ``` code block."""

    return DOCSTRING_SYSTEM_PROMPT, user_prompt
