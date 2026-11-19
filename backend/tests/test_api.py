"""API integration tests for FastAPI backend."""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health_endpoint():
    """Verify health endpoint returns valid state and model info."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "active_model" in data
    assert isinstance(data["supported_models"], list)


def test_samples_endpoint():
    """Verify samples listing and retrieval."""
    response = client.get("/api/samples")
    assert response.status_code == 200
    samples = response.json()
    assert len(samples) >= 4
    assert any("Grade" in s["name"] for s in samples)

    # Test single sample
    first_name = samples[0]["name"]
    res_single = client.get(f"/api/samples/{first_name}")
    assert res_single.status_code == 200
    assert res_single.json()["name"] == first_name


def test_analyze_endpoint_valid():
    """Verify AST analysis via POST /api/analyze."""
    code = """def add(x, y):
    return x + y
"""
    response = client.post("/api/analyze", json={"code": code})
    assert response.status_code == 200
    data = response.json()
    assert data["syntax_valid"] is True
    assert "metrics" in data
    assert data["metrics"]["functions_count"] == 1


def test_analyze_endpoint_syntax_error():
    """Verify syntax error reporting via POST /api/analyze."""
    bad_code = "def bad(x\n  return x"
    response = client.post("/api/analyze", json={"code": bad_code})
    assert response.status_code == 200
    data = response.json()
    assert data["syntax_valid"] is False
    assert len(data["issues"]) > 0


def test_validate_syntax_action():
    """Verify syntax check action via POST /api/validate."""
    code = "def valid():\n    return 42"
    response = client.post("/api/validate", json={"code": code, "action": "validate"})
    assert response.status_code == 200
    assert response.json()["syntax_valid"] is True


def test_validate_format_black_action():
    """Verify Black formatting action via POST /api/validate."""
    unformatted = "def foo( x,y ):\n  z=x+y\n  return z"
    response = client.post("/api/validate", json={"code": unformatted, "action": "format_black"})
    assert response.status_code == 200
    data = response.json()
    assert "def foo(x, y):" in data["formatted_code"]


def test_validate_run_tests_action():
    """Verify isolated test suite execution via POST /api/validate."""
    code = "def multiply(a, b):\n    return a * b\n"
    tests = "assert multiply(3, 4) == 12"
    response = client.post("/api/validate", json={"code": code, "test_code": tests, "action": "run_tests"})
    assert response.status_code == 200
    data = response.json()
    assert data["syntax_valid"] is True
    assert data["test_result"]["passed"] is True


def test_empty_input_errors():
    """Verify 400 Bad Request on empty code inputs."""
    res_analyze = client.post("/api/analyze", json={"code": ""})
    assert res_analyze.status_code == 400

    res_refactor = client.post("/api/refactor", json={"code": "   "})
    assert res_refactor.status_code == 400
