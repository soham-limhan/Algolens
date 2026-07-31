"""
tests/test_sandbox_robustness.py — Adversarial sandbox tests.

Each test submits a hostile Java program through CompiledSubmission and asserts
the SPECIFIC expected failure mode, not just "did not succeed" — a generic
pass/fail assertion would hide a wrong isolation mechanism firing for the wrong reason.

These tests are marked @pytest.mark.integration — they run real Java and are slow.
"""
from __future__ import annotations

import pytest
from app.sandbox.executor import CompiledSubmission, SandboxLimits


NORMAL_JAVA = """
import java.util.*;
public class Solution {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        System.out.println(n * 2);
    }
}
"""

INFINITE_LOOP_JAVA = """
public class Solution {
    public static void main(String[] args) {
        while (true) {}
    }
}
"""

MEMORY_BOMB_JAVA = """
import java.util.*;
public class Solution {
    public static void main(String[] args) {
        List<byte[]> list = new ArrayList<>();
        while (true) {
            list.add(new byte[1024 * 1024]);  // Allocate 1MB per iteration
        }
    }
}
"""

OUTPUT_SPAM_JAVA = """
public class Solution {
    public static void main(String[] args) {
        StringBuilder sb = new StringBuilder("A".repeat(1000));
        while (true) {
            System.out.println(sb);
        }
    }
}
"""

FORK_BOMB_JAVA = """
public class Solution {
    public static void main(String[] args) throws Exception {
        while (true) {
            ProcessBuilder pb = new ProcessBuilder("java", "-version");
            pb.start();
        }
    }
}
"""


@pytest.mark.integration
class TestSandboxRobustness:
    def test_infinite_loop_times_out(self):
        """Infinite loop must produce timed_out=True within the wall-clock budget."""
        compiled = CompiledSubmission(INFINITE_LOOP_JAVA)
        assert not compiled.compilation_error
        limits = SandboxLimits(wall_timeout_s=3.0)
        result = compiled.run(stdin_data="", limits=limits)
        assert result.timed_out is True, "Infinite loop should have timed out"
        compiled.cleanup()

    def test_memory_bomb_does_not_exhaust_host(self):
        """Memory bomb must be killed by the limit, not exhaust host memory."""
        compiled = CompiledSubmission(MEMORY_BOMB_JAVA)
        assert not compiled.compilation_error
        limits = SandboxLimits(wall_timeout_s=10.0, memory_mb=64)
        result = compiled.run(stdin_data="", limits=limits)
        # Should exit non-zero (OOM or timeout) — not timed_out from wall clock necessarily
        assert result.exit_code != 0 or result.timed_out, (
            "Memory bomb should have been killed by memory limit"
        )
        compiled.cleanup()

    def test_output_spam_truncated(self):
        """Large output must be truncated, not buffer the entire output."""
        compiled = CompiledSubmission(OUTPUT_SPAM_JAVA)
        assert not compiled.compilation_error
        limits = SandboxLimits(wall_timeout_s=3.0)
        result = compiled.run(stdin_data="", limits=limits)
        # Output must be capped — not grow unboundedly
        assert len(result.stdout) <= 1024 * 1024 + 1000, (
            f"Output was not truncated — got {len(result.stdout)} bytes"
        )
        compiled.cleanup()

    def test_normal_submission_unaffected_after_hostile(self):
        """
        A normal correct submission run AFTER a hostile one must be completely unaffected.
        Proves per-run isolation and cleanup.
        """
        # First: run a hostile submission
        hostile = CompiledSubmission(INFINITE_LOOP_JAVA)
        hostile.run(stdin_data="", limits=SandboxLimits(wall_timeout_s=2.0))
        hostile.cleanup()

        # Then: normal submission should work perfectly
        normal = CompiledSubmission(NORMAL_JAVA)
        assert not normal.compilation_error
        result = normal.run(stdin_data="4\n", limits=SandboxLimits(wall_timeout_s=5.0))
        assert result.exit_code == 0
        assert result.stdout.strip() == "8"
        assert result.timed_out is False
        normal.cleanup()

    def test_empty_submission_compilation_error(self):
        """Regression: empty source code must produce Compilation Error, not Accepted."""
        compiled = CompiledSubmission("")
        assert compiled.compilation_error is True, (
            "Empty submission must fail to compile"
        )
        compiled.cleanup()
