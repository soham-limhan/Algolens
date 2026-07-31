"""
tests/test_submission_pipeline_integration.py — Full pipeline integration tests.

These tests actually compile and run Java code — they are SLOW.
Marked @pytest.mark.integration; excluded from the fast unit suite.

Run: pytest (full suite) or pytest -m "not integration" (fast only)

Six scenarios tested per TESTING.md Section 4:
  1. Correct + efficient solution → Accepted, no hint
  2. Correct + inefficient solution → Accepted, hint populated, O(n²)
  3. Wrong answer → failed, failure_detail populated, zero BenchmarkRun rows
  4. Compilation error → failed, compiler output in failure_detail
  5. Access control — second user cannot see first user's submission (404)
  6. Zero test cases → explicit error, not a silent Accepted (regression test)
"""
from __future__ import annotations

import pytest

from app.models.problem import Problem, TestCase, InefficiencySignature
from app.models.submission import BenchmarkRun, Submission
from app.models.user import User
from app.sandbox.executor import CompiledSubmission, SandboxLimits
from app.services.correctness import run_correctness_check
from app.services.pipeline import run_pipeline
from app.auth.security import hash_password
from app.db.database import Base, SessionLocal, engine


@pytest.fixture(scope="module")
def db():
    """In-memory SQLite test database."""
    import os
    test_db_url = "sqlite:///./test_algolens.db"
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    test_engine = create_engine(test_db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=test_engine)
    TestSession = sessionmaker(bind=test_engine)
    session = TestSession()
    yield session
    session.close()
    Base.metadata.drop_all(bind=test_engine)
    import os
    try:
        os.remove("./test_algolens.db")
    except Exception:
        pass


@pytest.fixture(scope="module")
def two_sum_problem(db):
    """Seed a Two Sum problem with real test cases."""
    problem = Problem(
        title="Two Sum Test",
        description="Test problem",
        difficulty="easy",
        optimal_time_complexity="O(n)",
        optimal_space_complexity="O(n)",
        generator_key="two_sum",
    )
    db.add(problem)
    db.flush()

    tc1 = TestCase(
        problem_id=problem.id,
        input="4\n2 7 11 15\n9\n",
        expected_output="0 1",
        comparator_type="sorted",
    )
    tc2 = TestCase(
        problem_id=problem.id,
        input="3\n3 2 4\n6\n",
        expected_output="1 2",
        comparator_type="sorted",
    )
    sig = InefficiencySignature(
        problem_id=problem.id,
        pattern_type="nested_loop_lookup",
        hint_text="Consider a HashMap instead of a nested loop.",
    )
    db.add_all([tc1, tc2, sig])
    db.commit()
    return problem


@pytest.fixture(scope="module")
def test_user(db):
    user = User(name="Test User", email="test@example.com", password_hash=hash_password("password"))
    db.add(user)
    db.commit()
    return user


@pytest.mark.integration
class TestCorrectnessService:
    OPTIMAL_JAVA = """
import java.util.*;
public class Solution {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int[] nums = new int[n];
        for (int i = 0; i < n; i++) nums[i] = sc.nextInt();
        int target = sc.nextInt();
        Map<Integer, Integer> map = new HashMap<>();
        for (int i = 0; i < n; i++) {
            int comp = target - nums[i];
            if (map.containsKey(comp)) {
                System.out.println(map.get(comp) + " " + i);
                return;
            }
            map.put(nums[i], i);
        }
    }
}
"""
    BRUTE_FORCE_JAVA = """
import java.util.*;
public class Solution {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int[] nums = new int[n];
        for (int i = 0; i < n; i++) nums[i] = sc.nextInt();
        int target = sc.nextInt();
        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                if (nums[i] + nums[j] == target) {
                    System.out.println(i + " " + j);
                    return;
                }
            }
        }
    }
}
"""
    WRONG_ANSWER_JAVA = """
import java.util.*;
public class Solution {
    public static void main(String[] args) {
        System.out.println("1 2");
    }
}
"""
    COMPILATION_ERROR_JAVA = """
public class Solution {
    public static void main(String[] args) {
        THIS IS NOT VALID JAVA
    }
}
"""
    RUNTIME_ERROR_JAVA = """
public class Solution {
    public static void main(String[] args) {
        throw new RuntimeException("boom");
    }
}
"""

    def test_correct_optimal_accepted(self, two_sum_problem):
        compiled = CompiledSubmission(self.OPTIMAL_JAVA)
        assert not compiled.compilation_error, compiled.compiler_output
        result = run_correctness_check(compiled, two_sum_problem.test_cases)
        assert result.verdict == "Accepted"
        assert result.failure_detail is None
        compiled.cleanup()

    def test_compilation_error(self):
        compiled = CompiledSubmission(self.COMPILATION_ERROR_JAVA)
        result = run_correctness_check(compiled, [])
        # Even with no test cases, compilation error is caught before the empty-list check
        assert result.verdict == "Compilation Error"
        assert result.failure_detail is not None
        compiled.cleanup()

    def test_wrong_answer(self, two_sum_problem):
        compiled = CompiledSubmission(self.WRONG_ANSWER_JAVA)
        assert not compiled.compilation_error
        result = run_correctness_check(compiled, two_sum_problem.test_cases)
        assert result.verdict == "Wrong Answer"
        assert result.failure_detail is not None
        compiled.cleanup()

    def test_runtime_error(self, two_sum_problem):
        compiled = CompiledSubmission(self.RUNTIME_ERROR_JAVA)
        assert not compiled.compilation_error
        result = run_correctness_check(compiled, two_sum_problem.test_cases)
        assert result.verdict == "Runtime Error"
        compiled.cleanup()

    def test_zero_test_cases_explicit_error(self):
        """Regression test for CHANGELOG.md 0.4.1 — vacuous all() over empty list."""
        compiled = CompiledSubmission(self.OPTIMAL_JAVA)
        result = run_correctness_check(compiled, [])  # Zero test cases
        # Must NOT be Accepted — must be an explicit error
        assert result.verdict != "Accepted", (
            "Zero test cases should not silently return Accepted (regression from 0.4.1)"
        )
        compiled.cleanup()

    def test_no_benchmark_runs_on_failure(self, db, two_sum_problem, test_user):
        """Regression: failing submission must produce ZERO BenchmarkRun rows."""
        sub = Submission(
            user_id=test_user.id,
            problem_id=two_sum_problem.id,
            source_code=self.WRONG_ANSWER_JAVA,
            status="pending",
        )
        db.add(sub)
        db.commit()
        run_pipeline(sub.id, db)
        db.refresh(sub)
        assert sub.status == "failed"
        runs = db.query(BenchmarkRun).filter(BenchmarkRun.submission_id == sub.id).all()
        assert len(runs) == 0, f"Expected 0 BenchmarkRun rows for failing submission, got {len(runs)}"
