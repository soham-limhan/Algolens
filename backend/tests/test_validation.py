"""
tests/test_validation.py — Unit and endpoint validation tests based on VALIDATIONS.md.
"""
from __future__ import annotations

import uuid
import pytest
from fastapi.testclient import TestClient

from app.auth import router as auth_router
from app.auth.dependencies import get_current_user
from app.config import Settings
from app.main import app
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest
from app.schemas.submission import SubmissionCreate
from app.seed import validate_problem_data

client = TestClient(app)


# ── Auth Schema & Endpoint Validation Tests ───────────────────────────────────

def test_register_empty_or_whitespace_name_rejected():
    with pytest.raises(ValueError, match="Name must be between 1 and 120 characters"):
        RegisterRequest(name="   ", email="user@example.com", password="password123")


def test_register_overly_long_name_rejected():
    long_name = "a" * 121
    with pytest.raises(ValueError):
        RegisterRequest(name=long_name, email="user@example.com", password="password123")


def test_register_malformed_email_rejected():
    with pytest.raises(ValueError):
        RegisterRequest(name="Valid User", email="not-an-email", password="password123")


def test_register_password_short_rejected():
    with pytest.raises(ValueError, match="at least 8 characters"):
        RegisterRequest(name="Valid User", email="user@example.com", password="short")


def test_register_password_over_128_rejected():
    long_pass = "a" * 129
    with pytest.raises(ValueError, match="at most 128 characters"):
        RegisterRequest(name="Valid User", email="user@example.com", password=long_pass)


def test_register_password_exactly_8_accepted():
    req = RegisterRequest(name="Valid User", email="USER@Example.COM", password="12345678")
    assert req.email == "user@example.com"
    assert req.password == "12345678"


def test_login_schema_normalizes_email():
    req = LoginRequest(email="  TEST@Example.COM  ", password="any")
    assert req.email == "test@example.com"


def test_forgot_password_generates_otp_for_existing_email():
    email = f"otp-{uuid.uuid4()}@example.com"
    register_response = client.post(
        "/auth/register",
        json={"name": "OTP User", "email": email, "password": "password123"},
    )
    assert register_response.status_code == 201

    response = client.post("/auth/forgot-password", json={"email": email})
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "OTP generated successfully"
    assert auth_router._otp_store[email.lower()]


def test_forgot_password_returns_error_for_missing_email():
    response = client.post(
        "/auth/forgot-password",
        json={"email": f"missing-{uuid.uuid4()}@example.com"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Email does not exist"


def test_verify_otp_and_reset_password_flow():
    email = f"reset-{uuid.uuid4()}@example.com"
    register_response = client.post(
        "/auth/register",
        json={"name": "Reset User", "email": email, "password": "password123"},
    )
    assert register_response.status_code == 201

    forgot_response = client.post("/auth/forgot-password", json={"email": email})
    assert forgot_response.status_code == 200
    otp = auth_router._otp_store[email.lower()]

    verify_response = client.post("/auth/verify-otp", json={"email": email, "otp": otp})
    assert verify_response.status_code == 200
    assert verify_response.json()["message"] == "OTP verified successfully"

    reset_response = client.post(
        "/auth/reset-password",
        json={"email": email, "otp": otp, "new_password": "newpassword123"},
    )
    assert reset_response.status_code == 200
    assert reset_response.json()["message"] == "Password updated successfully"

    login_response = client.post(
        "/auth/login",
        json={"email": email, "password": "newpassword123"},
    )
    assert login_response.status_code == 200


def test_create_problem_endpoint():
    payload = {
        "title": "3Sum Closest",
        "description": "Given an integer array nums...",
        "difficulty": "medium",
        "optimal_time_complexity": "O(n^2)",
        "optimal_space_complexity": "O(1)",
        "generator_key": "two_sum",
        "test_cases": [{"input": "[-1,2,1,-4]\n1", "expected_output": "2"}]
    }
    response = client.post("/problems", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "3Sum Closest"
    assert data["difficulty"] == "medium"
    assert len(data["test_cases"]) == 1


# ── Submission Schema Validation Tests ────────────────────────────────────────

def test_submission_create_invalid_uuid_rejected():
    with pytest.raises(ValueError, match="problem_id must be a valid UUID"):
        SubmissionCreate(problem_id="not-a-uuid", source_code="public class Solution {}")


def test_submission_create_empty_code_rejected():
    valid_uuid = str(uuid.uuid4())
    with pytest.raises(ValueError, match="cannot be empty"):
        SubmissionCreate(problem_id=valid_uuid, source_code="   \n\t  ")


def test_submission_create_over_max_size_rejected():
    valid_uuid = str(uuid.uuid4())
    huge_code = "x" * 65537
    with pytest.raises(ValueError, match="source code exceeds maximum length"):
        SubmissionCreate(problem_id=valid_uuid, source_code=huge_code)


# ── API Error Format & Query Parameter Boundary Tests ─────────────────────────

def test_api_validation_error_format_and_status():
    response = client.post("/auth/register", json={"name": "", "email": "invalid", "password": "123"})
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert isinstance(data["detail"], list)
    for err in data["detail"]:
        assert "field" in err
        assert "message" in err


def test_invalid_uuid_path_param_rejected():
    response = client.get("/problems/not-a-valid-uuid")
    assert response.status_code == 422
    data = response.json()
    assert data["detail"][0]["field"] == "problem_id"


def test_history_query_pagination_limits():
    valid_user_id = str(uuid.uuid4())
    mock_user = User(id=valid_user_id, name="Test User", email="test@example.com", password_hash="hash")
    app.dependency_overrides[get_current_user] = lambda: mock_user

    try:
        # limit = 0 -> rejected (ge=1)
        res_zero = client.get(f"/users/{valid_user_id}/history?limit=0")
        assert res_zero.status_code == 422

        # limit = 101 -> rejected (le=100)
        res_over = client.get(f"/users/{valid_user_id}/history?limit=101")
        assert res_over.status_code == 422

        # offset = -1 -> rejected (ge=0)
        res_neg = client.get(f"/users/{valid_user_id}/history?offset=-1")
        assert res_neg.status_code == 422
    finally:
        app.dependency_overrides.pop(get_current_user, None)


# ── Seed-Time Data Sanity Validation Tests ───────────────────────────────────

def test_validate_problem_data_accepts_valid():
    valid_prob = {
        "title": "Test Title",
        "description": "Test description",
        "difficulty": "easy",
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(1)",
        "generator_key": "two_sum",
        "test_cases": [{"input": "1\n", "expected_output": "1\n", "comparator_type": "exact"}],
        "signatures": [{"pattern_type": "nested_loop_lookup", "hint_text": "hint"}],
    }
    # Should pass cleanly without raising
    validate_problem_data(valid_prob)


def test_validate_problem_data_rejects_invalid_difficulty():
    bad_prob = {
        "title": "Bad Diff",
        "description": "desc",
        "difficulty": "super_hard",
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(1)",
        "generator_key": "two_sum",
    }
    with pytest.raises(ValueError, match="invalid difficulty"):
        validate_problem_data(bad_prob)


def test_validate_problem_data_rejects_invalid_complexity():
    bad_prob = {
        "title": "Bad Complexity",
        "description": "desc",
        "difficulty": "easy",
        "optimal_time_complexity": "O(n^4)",  # Not in COMPLEXITY_ORDER
        "optimal_space_complexity": "O(1)",
        "generator_key": "two_sum",
    }
    with pytest.raises(ValueError, match="invalid optimal_time_complexity"):
        validate_problem_data(bad_prob)


def test_validate_problem_data_rejects_unregistered_generator():
    bad_prob = {
        "title": "Bad Generator",
        "description": "desc",
        "difficulty": "easy",
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(1)",
        "generator_key": "unregistered_key",
    }
    with pytest.raises(ValueError, match="unregistered generator_key"):
        validate_problem_data(bad_prob)


def test_validate_problem_data_rejects_unregistered_pattern_type():
    bad_prob = {
        "title": "Bad Signature",
        "description": "desc",
        "difficulty": "easy",
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(1)",
        "generator_key": "two_sum",
        "signatures": [{"pattern_type": "unknown_pattern", "hint_text": "hint"}],
    }
    with pytest.raises(ValueError, match="unregistered pattern_type"):
        validate_problem_data(bad_prob)


# ── Configuration Startup Fail-Fast Validation Tests ────────────────────────

def test_config_invalid_benchmark_sizes():
    with pytest.raises(ValueError, match="strictly ascending order"):
        Settings(benchmark_input_sizes="100,50,200")

    with pytest.raises(ValueError, match="positive integers"):
        Settings(benchmark_input_sizes="-100,500")


def test_config_invalid_database_url():
    with pytest.raises(ValueError, match="DATABASE_URL must be a valid"):
        Settings(database_url="mysql://localhost/algolens")
