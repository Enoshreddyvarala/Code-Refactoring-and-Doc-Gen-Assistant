"""Unit tests for Python AST code analyzer in CodeMate AI."""

import pytest
from services.code_analyzer import analyze_code, _calculate_health_score


def test_syntax_error_detection():
    invalid_code = "def bad_syntax(x\n    return x + 1"
    result = analyze_code(invalid_code)

    assert result["syntax_valid"] is False
    assert result["error"] is not None
    assert len(result["issues"]) > 0
    assert result["issues"][0]["severity"] == "Critical"
    assert "Syntax Error" in result["issues"][0]["title"]


def test_missing_docstrings_detection():
    code_without_docstring = """def add_numbers(a, b):
    return a + b

class MathEngine:
    def multiply(self, x, y):
        return x * y
"""
    result = analyze_code(code_without_docstring)
    assert result["syntax_valid"] is True

    docstring_issues = [i for i in result["issues"] if i["category"] == "Documentation"]
    # Expect 1 function, 1 class, 1 method
    assert len(docstring_issues) >= 2


def test_unused_imports_detection():
    code_with_unused = """import os
import math

def calculate_square(x):
    return math.sqrt(x)
"""
    result = analyze_code(code_with_unused)
    assert result["syntax_valid"] is True

    import_issues = [i for i in result["issues"] if "Potentially Unused Import" in i["title"]]
    assert len(import_issues) == 1
    assert "os" in import_issues[0]["title"]


def test_naming_conventions():
    bad_names_code = """class my_calculator:
    def CalculateSum(self, a, b):
        return a + b
"""
    result = analyze_code(bad_names_code)
    assert result["syntax_valid"] is True

    naming_issues = [i for i in result["issues"] if i["category"] == "Naming Conventions"]
    assert len(naming_issues) >= 2  # class name and function name both non-standard


def test_mutable_default_argument():
    code_with_mutable_default = """def append_item(val, container=[]):
    container.append(val)
    return container
"""
    result = analyze_code(code_with_mutable_default)
    assert result["syntax_valid"] is True

    smell_issues = [i for i in result["issues"] if "Mutable Default Argument" in i["title"]]
    assert len(smell_issues) == 1


def test_bare_except_detection():
    code_with_bare_except = """try:
    val = int("abc")
except:
    val = 0
"""
    result = analyze_code(code_with_bare_except)
    assert result["syntax_valid"] is True

    bare_except_issues = [i for i in result["issues"] if "Bare 'except:'" in i["title"]]
    assert len(bare_except_issues) == 1


def test_deep_nesting_detection():
    deep_nested_code = """def deep_function(x):
    if x > 0:
        for i in range(x):
            if i % 2 == 0:
                for j in range(i):
                    if j == 3:
                        print("deep")
"""
    result = analyze_code(deep_nested_code)
    assert result["syntax_valid"] is True

    nesting_issues = [i for i in result["issues"] if "Deep Nesting" in i["title"]]
    assert len(nesting_issues) >= 1


def test_metrics_and_health_score():
    clean_code = '''"""Module docstring."""

def compute_total(price: float, tax: float) -> float:
    """Calculate total price including tax.

    Args:
        price: Base item price.
        tax: Applicable tax rate.

    Returns:
        Final calculated price.
    """
    return price + (price * tax)
'''
    result = analyze_code(clean_code)
    assert result["syntax_valid"] is True
    assert result["metrics"]["functions_count"] == 1
    assert result["health_score"] >= 80  # Clean code receives high score
