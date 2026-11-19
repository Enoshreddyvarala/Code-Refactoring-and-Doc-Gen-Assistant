"""Validation and Safe Test Runner Service for CodeMate AI.

Enforces safe evaluation:
- AST syntax validation and compilation check
- Black code formatting
- Isolated subprocess test execution (never inside the Streamlit process)
- Clear distinction between syntax validity and behavioral equivalence
"""

import ast
import subprocess
import sys
import tempfile
import time
from typing import Any, Dict, Optional, Tuple

try:
    import black
    BLACK_AVAILABLE = True
except ImportError:
    BLACK_AVAILABLE = False


def validate_syntax(code: str) -> Dict[str, Any]:
    """Validate Python code syntax using AST parsing and compilation check.

    Args:
        code: Python source code string.

    Returns:
        Dict containing valid status, error details, and extracted AST symbols.
    """
    if not code or not code.strip():
        return {
            "valid": False,
            "error": "Code is empty.",
            "error_type": "EmptyInput",
            "line": None,
            "column": None,
            "symbols": {}
        }

    try:
        tree = ast.parse(code)
        # Verify it can be compiled to bytecode
        compile(code, "<string>", "exec")

        # Collect top-level symbols
        functions = [n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]

        return {
            "valid": True,
            "error": None,
            "error_type": None,
            "line": None,
            "column": None,
            "symbols": {
                "functions": functions,
                "classes": classes
            }
        }
    except SyntaxError as exc:
        return {
            "valid": False,
            "error": exc.msg,
            "error_type": "SyntaxError",
            "line": exc.lineno,
            "column": exc.offset,
            "offending_line": exc.text.strip() if exc.text else "",
            "symbols": {}
        }
    except Exception as exc:
        return {
            "valid": False,
            "error": str(exc),
            "error_type": type(exc).__name__,
            "line": None,
            "column": None,
            "symbols": {}
        }


def format_with_black(code: str) -> Tuple[bool, str, str]:
    """Format Python code using Black.

    Args:
        code: Unformatted Python source code.

    Returns:
        Tuple of (success, formatted_code_or_original, message).
    """
    if not BLACK_AVAILABLE:
        return False, code, "Black formatter is not installed in the environment."

    if not code or not code.strip():
        return False, code, "Cannot format empty code."

    try:
        formatted = black.format_str(code, mode=black.FileMode())
        if formatted.strip() == code.strip():
            return True, formatted, "Code is already perfectly formatted with Black!"
        return True, formatted, "Successfully formatted code with Black PEP 8 standards."
    except black.InvalidInput as inv_err:
        return False, code, f"Black formatting failed due to syntax error: {str(inv_err)}"
    except Exception as exc:
        return False, code, f"Black formatting error: {str(exc)}"


def run_isolated_test_suite(code: str, test_code: str, timeout_seconds: float = 3.0) -> Dict[str, Any]:
    """Execute test assertions in an isolated subprocess.

    CRITICAL SECURITY DESIGN:
    Arbitrary user code is NEVER executed inside the Streamlit host process.
    Execution occurs in a temporary file executed by a separate Python subprocess
    with strict timeout constraints.

    Args:
        code: The base Python source code to test.
        test_code: Test cases or assertions (e.g., 'assert add(2, 3) == 5').
        timeout_seconds: Subprocess timeout threshold.

    Returns:
        Dict containing passed status, output, errors, duration, and safety disclaimer.
    """
    # 1. AST pre-check on both base and test code
    base_val = validate_syntax(code)
    if not base_val["valid"]:
        return {
            "passed": False,
            "error": f"Base code has syntax error at line {base_val.get('line')}: {base_val.get('error')}",
            "stdout": "",
            "duration": 0.0,
            "status": "Syntax Error in Code"
        }

    test_val = validate_syntax(test_code)
    if not test_val["valid"]:
        return {
            "passed": False,
            "error": f"Test code has syntax error at line {test_val.get('line')}: {test_val.get('error')}",
            "stdout": "",
            "duration": 0.0,
            "status": "Syntax Error in Tests"
        }

    # 2. Combine into temporary script
    combined_script = f"""# Isolated Test Runner Script
{code}

# --- User Test Suite ---
{test_code}
"""

    start_time = time.time()
    temp_file_path = None

    try:
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as tmp:
            temp_file_path = tmp.name
            tmp.write(combined_script)

        # 3. Execute in isolated subprocess
        process = subprocess.run(
            [sys.executable, temp_file_path],
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
        duration = round(time.time() - start_time, 3)

        if process.returncode == 0:
            return {
                "passed": True,
                "error": None,
                "stdout": process.stdout.strip() or "All assertions and tests passed successfully!",
                "duration": duration,
                "status": "Passed"
            }
        else:
            stderr_out = process.stderr.strip()
            return {
                "passed": False,
                "error": stderr_out or "Subprocess exited with a non-zero exit code.",
                "stdout": process.stdout.strip(),
                "duration": duration,
                "status": "Failed"
            }

    except subprocess.TimeoutExpired:
        duration = round(time.time() - start_time, 3)
        return {
            "passed": False,
            "error": f"Execution timed out after {timeout_seconds} seconds. Possible infinite loop detected.",
            "stdout": "",
            "duration": duration,
            "status": "Timeout"
        }
    except Exception as exc:
        return {
            "passed": False,
            "error": f"Failed to execute isolated test suite: {str(exc)}",
            "stdout": "",
            "duration": 0.0,
            "status": "Execution Error"
        }
    finally:
        # Cleanup temporary test file safely
        if temp_file_path:
            try:
                import os
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
            except Exception:
                pass
