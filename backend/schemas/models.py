"""Pydantic schemas for CodeMate AI FastAPI backend."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CodeRequest(BaseModel):
    """Standard request payload containing Python source code."""
    code: str = Field(..., description="Python source code to process")
    model: Optional[str] = Field(None, description="Optional Gemini model override")
    api_key: Optional[str] = Field(None, description="Optional user-provided Gemini API key")


class AnalysisResponse(BaseModel):
    """Response payload for AST and Black code analysis."""
    syntax_valid: bool
    health_score: int
    metrics: Dict[str, Any]
    issues: List[Dict[str, Any]]
    black_compliant: bool
    black_message: str
    disclaimer: str
    error: Optional[str] = None


class RefactorResponse(BaseModel):
    """Response payload for AI-powered code refactoring."""
    success: bool
    is_syntax_valid: bool
    syntax_error: Optional[str] = None
    original_code: str
    refactored_code: str
    explanation: str
    diff: str
    original_analysis: Dict[str, Any]
    refactored_analysis: Dict[str, Any]
    health_score_delta: int
    error: Optional[str] = None


class ExplainResponse(BaseModel):
    """Response payload for beginner-friendly code explanation."""
    success: bool
    has_syntax_warning: bool
    syntax_warning_message: Optional[str] = None
    explanation: str
    error: Optional[str] = None


class DocRequest(BaseModel):
    """Request payload for documentation generation."""
    code: str = Field(..., description="Python source code")
    doc_type: str = Field("all", description="Type of docs: 'readme', 'docstrings', or 'all'")
    model: Optional[str] = None
    api_key: Optional[str] = None


class DocResponse(BaseModel):
    """Response payload for documentation generation."""
    success: bool
    readme_markdown: Optional[str] = None
    documented_code: Optional[str] = None
    is_syntax_valid: Optional[bool] = None
    error: Optional[str] = None


class ValidationRequest(BaseModel):
    """Request payload for code validation, formatting, or isolated testing."""
    code: str = Field(..., description="Base Python source code")
    test_code: Optional[str] = Field(None, description="Optional assertion script to execute")
    action: str = Field("validate", description="'validate', 'format_black', or 'run_tests'")


class ValidationResponse(BaseModel):
    """Response payload for validation and testing actions."""
    syntax_valid: bool
    error: Optional[str] = None
    line: Optional[int] = None
    column: Optional[int] = None
    symbols: Optional[Dict[str, Any]] = None
    formatted_code: Optional[str] = None
    black_message: Optional[str] = None
    test_result: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Service health and capability status."""
    status: str
    version: str
    gemini_configured: bool
    active_model: str
    supported_models: List[str]


class SampleItem(BaseModel):
    """Sample program description and code."""
    name: str
    description: str
    code: str
