"""Unit tests for validation and isolated test execution in CodeMate AI."""

import pytest
from services.validation_service import (
    validate_syntax,
    format_with_black,
    run_isolated_test_suite,
)
from utils.file_handler import extract_python_code, generate_diff


def test_validate_syntax_valid():
    code = "def greet(name: str) -> str:\n    return f'Hello, {name}'\n"
    res = validate_syntax(code)
    assert res["valid"] is True
    assert res["error"] is None
    assert "greet" in res["symbols"]["functions"]


def test_validate_syntax_invalid():
    bad_code = "def broken(\n    print('missing paren')"
    res = validate_syntax(bad_code)
    assert res["valid"] is False
    assert res["error"] is not None
    assert res["line"] is not None


def test_validate_syntax_empty():
    res = validate_syntax("   ")
    assert res["valid"] is False
    assert res["error_type"] == "EmptyInput"


def test_black_formatting():
    unformatted = "def foo(   x,y ):\n  z=x+y\n  return z"
    success, formatted, msg = format_with_black(unformatted)
    assert success is True
    assert "def foo(x, y):" in formatted
    assert "z = x + y" in formatted


def test_isolated_test_runner_success():
    code = """def add(a, b):
    return a + b
"""
    test_cases = """assert add(2, 3) == 5
assert add(-1, 1) == 0
"""
    result = run_isolated_test_suite(code, test_cases, timeout_seconds=2.0)
    assert result["passed"] is True
    assert result["error"] is None
    assert result["status"] == "Passed"


def test_isolated_test_runner_failure():
    code = """def add(a, b):
    return a - b  # Bug intentional
"""
    test_cases = """assert add(2, 3) == 5"""
    result = run_isolated_test_suite(code, test_cases, timeout_seconds=2.0)
    assert result["passed"] is False
    assert "AssertionError" in result["error"]
    assert result["status"] == "Failed"


def test_isolated_test_runner_timeout():
    infinite_loop_code = """def loop_forever():
    while True:
        pass
"""
    test_cases = "loop_forever()"
    # Use a short timeout of 1.0s
    result = run_isolated_test_suite(infinite_loop_code, test_cases, timeout_seconds=1.0)
    assert result["passed"] is False
    assert result["status"] == "Timeout"


def test_extract_python_code_markdown():
    markdown = """Here is the refactored code:
```python
def clean():
    return 42
```
Hope that helps!
"""
    extracted = extract_python_code(markdown)
    assert extracted.strip() == "def clean():\n    return 42"


def test_generate_diff():
    code1 = "x = 1\ny = 2\n"
    code2 = "x = 1\ny = 3\n"
    diff = generate_diff(code1, code2)
    assert "-y = 2" in diff
    assert "+y = 3" in diff
