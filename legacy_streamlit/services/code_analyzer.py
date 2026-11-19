"""Code Analyzer Service for CodeMate AI.

Leverages Python's native AST (Abstract Syntax Tree) and Black to analyze:
- Syntax validity and compile checks
- Missing docstrings in classes, functions, and methods
- Unused imports (where statically determinable)
- Overly long functions
- Naming convention violations (PEP 8)
- Structural issues (mutable defaults, bare excepts, deep nesting)
- Cyclomatic complexity estimates and health scoring
"""

import ast
import re
from typing import Any, Dict, List, Optional, Set, Tuple

try:
    import black
    BLACK_AVAILABLE = True
except ImportError:
    BLACK_AVAILABLE = False


MAX_RECOMMENDED_FUNCTION_LINES = 25
MAX_RECOMMENDED_PARAMS = 5
MAX_RECOMMENDED_NESTING = 3


class ASTVisitor(ast.NodeVisitor):
    """AST visitor traversing Python code to extract issues and structural metrics."""

    def __init__(self, raw_code: str):
        self.raw_code = raw_code
        self.issues: List[Dict[str, Any]] = []
        self.functions_count = 0
        self.classes_count = 0
        self.imports_count = 0
        self.complexity_score = 1  # Base complexity

        # Import tracking
        self.imported_names: Dict[str, Tuple[int, str]] = {}  # name -> (lineno, module)
        self.used_names: Set[str] = set()

        # Nesting tracking
        self.current_nesting = 0

    def visit_Import(self, node: ast.Import):
        self.imports_count += len(node.names)
        for alias in node.names:
            imported_identifier = alias.asname or alias.name.split(".")[0]
            self.imported_names[imported_identifier] = (node.lineno, alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        self.imports_count += len(node.names)
        module_name = node.module or ""
        for alias in node.names:
            if alias.name == "*":
                self.issues.append({
                    "severity": "Warning",
                    "category": "Style & Imports",
                    "title": "Wildcard Import Used",
                    "line": node.lineno,
                    "description": f"Using 'from {module_name} import *' pollutes the global namespace.",
                    "suggestion": "Explicitly import the required functions or classes instead of using '*'."
                })
                continue
            imported_identifier = alias.asname or alias.name
            self.imported_names[imported_identifier] = (node.lineno, f"{module_name}.{alias.name}")
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name):
        if isinstance(node.ctx, ast.Load):
            self.used_names.add(node.id)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        self.classes_count += 1

        # Check docstring
        docstring = ast.get_docstring(node)
        if not docstring:
            self.issues.append({
                "severity": "Info",
                "category": "Documentation",
                "title": f"Missing Class Docstring: '{node.name}'",
                "line": node.lineno,
                "description": f"Class '{node.name}' has no docstring explaining its responsibility.",
                "suggestion": "Add a PEP 257 docstring summarizing the class purpose and attributes."
            })

        # Check naming convention (PascalCase / CapWords)
        if not re.match(r"^[A-Z][a-zA-Z0-9]*$", node.name):
            self.issues.append({
                "severity": "Warning",
                "category": "Naming Conventions",
                "title": f"Non-PEP 8 Class Name: '{node.name}'",
                "line": node.lineno,
                "description": f"Class '{node.name}' does not follow the CapWords/PascalCase convention.",
                "suggestion": f"Rename '{node.name}' to PascalCase (e.g., '{node.name.capitalize()}')."
            })

        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._check_function(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self._check_function(node)
        self.generic_visit(node)

    def _check_function(self, node: Any):
        self.functions_count += 1

        # Docstring check
        docstring = ast.get_docstring(node)
        if not docstring and not node.name.startswith("__"):
            self.issues.append({
                "severity": "Info",
                "category": "Documentation",
                "title": f"Missing Function Docstring: '{node.name}()'",
                "line": node.lineno,
                "description": f"Function '{node.name}' lacks a docstring documenting its purpose and arguments.",
                "suggestion": "Add a docstring detailing parameters, return type, and expected behavior."
            })

        # Naming convention (snake_case)
        if not node.name.startswith("__") and not re.match(r"^_{0,2}[a-z][a-z0-9_]*$", node.name):
            self.issues.append({
                "severity": "Warning",
                "category": "Naming Conventions",
                "title": f"Non-PEP 8 Function Name: '{node.name}()'",
                "line": node.lineno,
                "description": f"Function '{node.name}' is not in lowercase snake_case.",
                "suggestion": "Use lowercase letters separated by underscores for function names."
            })

        # Function length check
        if hasattr(node, "end_lineno") and node.end_lineno:
            span = node.end_lineno - node.lineno + 1
            if span > MAX_RECOMMENDED_FUNCTION_LINES:
                self.issues.append({
                    "severity": "Warning",
                    "category": "Code Structure",
                    "title": f"Long Function: '{node.name}()' ({span} lines)",
                    "line": node.lineno,
                    "description": f"Function spans {span} lines (recommended maximum is {MAX_RECOMMENDED_FUNCTION_LINES}).",
                    "suggestion": "Decompose into smaller, single-purpose helper functions to enhance maintainability."
                })

        # Parameter count check
        total_args = len(node.args.args)
        if total_args > MAX_RECOMMENDED_PARAMS:
            self.issues.append({
                "severity": "Info",
                "category": "Code Structure",
                "title": f"Too Many Parameters in '{node.name}()' ({total_args} args)",
                "line": node.lineno,
                "description": f"Function takes {total_args} parameters, which can make it hard to test and maintain.",
                "suggestion": "Group related parameters into a dictionary, dataclass, or configuration object."
            })

        # Mutable default argument check
        for default in node.args.defaults:
            if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                self.issues.append({
                    "severity": "Warning",
                    "category": "Code Smells",
                    "title": f"Mutable Default Argument in '{node.name}()'",
                    "line": default.lineno,
                    "description": "Using a mutable object (list/dict/set) as a default argument leads to shared state bugs across calls.",
                    "suggestion": "Use 'default=None' and initialize inside the function (e.g., 'if arg is None: arg = []')."
                })

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        # Bare except check (except: without type)
        if node.type is None:
            self.issues.append({
                "severity": "Warning",
                "category": "Error Handling",
                "title": "Bare 'except:' Clause Detected",
                "line": node.lineno,
                "description": "Bare 'except:' catches all exceptions, including KeyboardInterrupt and SystemExit.",
                "suggestion": "Catch specific exceptions like 'except ValueError:' or at minimum 'except Exception:'."
            })
        self.generic_visit(node)

    # Complexity & Nesting Visitors
    def visit_If(self, node: ast.If):
        self.complexity_score += 1
        self._check_nesting(node)
        self.current_nesting += 1
        self.generic_visit(node)
        self.current_nesting -= 1

    def visit_For(self, node: ast.For):
        self.complexity_score += 1
        self._check_nesting(node)
        self.current_nesting += 1
        self.generic_visit(node)
        self.current_nesting -= 1

    def visit_While(self, node: ast.While):
        self.complexity_score += 1
        self._check_nesting(node)
        self.current_nesting += 1
        self.generic_visit(node)
        self.current_nesting -= 1

    def visit_Try(self, node: ast.Try):
        self.complexity_score += len(node.handlers)
        self.generic_visit(node)

    def visit_BoolOp(self, node: ast.BoolOp):
        # 'and' / 'or' operators add decision branch points
        self.complexity_score += len(node.values) - 1
        self.generic_visit(node)

    def _check_nesting(self, node: Any):
        if self.current_nesting >= MAX_RECOMMENDED_NESTING:
            self.issues.append({
                "severity": "Warning",
                "category": "Code Structure",
                "title": f"Deep Nesting Detected (Depth {self.current_nesting + 1})",
                "line": node.lineno,
                "description": "Deeply nested code increases cognitive load and makes testing complex.",
                "suggestion": "Use guard clauses (early returns) or extract inner logic into a helper function."
            })


def analyze_code(code: str) -> Dict[str, Any]:
    """Perform comprehensive static AST and Black analysis on Python source code.

    Args:
        code: Python source code string.

    Returns:
        Dictionary containing syntax_valid, issues, metrics, health_score,
        black_compliant, and disclaimer.
    """
    if not code or not code.strip():
        return {
            "syntax_valid": False,
            "error": "Empty code input provided.",
            "issues": [],
            "metrics": {},
            "health_score": 0,
            "black_compliant": False,
            "disclaimer": "No code provided to analyze."
        }

    # 1. Syntax Parsing Check
    try:
        tree = ast.parse(code)
    except SyntaxError as syn_err:
        line_num = syn_err.lineno or 1
        offset = syn_err.offset or 1
        offending_line = syn_err.text.strip() if syn_err.text else ""
        return {
            "syntax_valid": False,
            "error": f"SyntaxError at line {line_num}, col {offset}: {syn_err.msg}",
            "error_details": {
                "line": line_num,
                "column": offset,
                "message": syn_err.msg,
                "offending_line": offending_line,
            },
            "issues": [{
                "severity": "Critical",
                "category": "Syntax",
                "title": f"Syntax Error: {syn_err.msg}",
                "line": line_num,
                "description": f"Python could not parse this line: '{offending_line}'",
                "suggestion": "Check for missing colons, unbalanced brackets, or invalid keywords."
            }],
            "metrics": _calculate_line_metrics(code),
            "health_score": 20,
            "black_compliant": False,
            "disclaimer": "Syntax errors prevent full AST structural analysis."
        }

    # 2. AST Visitor Traversal
    visitor = ASTVisitor(code)
    visitor.visit(tree)

    # 3. Detect Unused Imports
    for name, (lineno, full_path) in visitor.imported_names.items():
        if name not in visitor.used_names:
            visitor.issues.append({
                "severity": "Info",
                "category": "Style & Imports",
                "title": f"Potentially Unused Import: '{full_path}'",
                "line": lineno,
                "description": f"Module/object '{name}' is imported but not referenced anywhere in the script.",
                "suggestion": f"Remove 'import {name}' if it is no longer required."
            })

    # 4. Black Formatting Compliance Check
    black_compliant = False
    black_message = "Black is not installed."
    if BLACK_AVAILABLE:
        try:
            formatted = black.format_str(code, mode=black.FileMode())
            black_compliant = (formatted.strip() == code.strip())
            black_message = "Code adheres to Black formatting." if black_compliant else "Code differs from Black PEP 8 formatting standards."
        except Exception as exc:
            black_compliant = False
            black_message = f"Black check encountered an issue: {str(exc)}"

    if not black_compliant and BLACK_AVAILABLE:
        visitor.issues.append({
            "severity": "Info",
            "category": "Formatting",
            "title": "Code Formatting Can Be Improved",
            "line": 1,
            "description": black_message,
            "suggestion": "Use CodeMate AI's 'Format with Black' button to automatically clean indentation and spacing."
        })

    # 5. Metrics & Health Score Calculation
    metrics = _calculate_line_metrics(code)
    metrics["functions_count"] = visitor.functions_count
    metrics["classes_count"] = visitor.classes_count
    metrics["imports_count"] = visitor.imports_count
    metrics["cyclomatic_complexity"] = visitor.complexity_score

    health_score = _calculate_health_score(visitor.issues)

    return {
        "syntax_valid": True,
        "error": None,
        "issues": visitor.issues,
        "metrics": metrics,
        "health_score": health_score,
        "black_compliant": black_compliant,
        "black_message": black_message,
        "disclaimer": "Note: AST analysis detects structural patterns, PEP 8 rules, and syntax. It does not replace runtime testing or guarantee semantic correctness."
    }


def _calculate_line_metrics(code: str) -> Dict[str, int]:
    """Calculate basic line count metrics."""
    lines = code.splitlines()
    total_loc = len(lines)
    blank_lines = sum(1 for line in lines if not line.strip())
    comment_lines = sum(1 for line in lines if line.strip().startswith("#"))
    code_lines = total_loc - blank_lines - comment_lines

    return {
        "loc": total_loc,
        "code_lines": max(0, code_lines),
        "comment_lines": comment_lines,
        "blank_lines": blank_lines,
    }


def _calculate_health_score(issues: List[Dict[str, Any]]) -> int:
    """Calculate an intuitive 0-100 Code Health Score."""
    score = 100
    for issue in issues:
        severity = issue.get("severity", "Info")
        if severity == "Critical":
            score -= 40
        elif severity == "Warning":
            score -= 10
        elif severity == "Info":
            score -= 3

    return max(10, min(100, score))
