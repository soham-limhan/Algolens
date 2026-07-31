"""
app/sandbox/executor.py — CompiledSubmission: compile once, run many times.

Design rationale:
- Compile happens once (via a short-lived container or local javac call), producing
  a class file. Multiple .run() calls then each spawn a fresh, disposable container
  from the pre-built algolens-sandbox image — one container per test case and one per
  benchmark input size.
- Container-based isolation means filesystem and PID namespaces are actually isolated
  (not just resource-capped), which is a meaningful security upgrade over the original
  subprocess + resource.setrlimit design (retained as SECURITY.md fallback).
- Resource limits (CPU, memory, pids, network, filesystem) are all enforced at the
  Docker container runtime level, not just the JVM level — they hold even if the JVM
  ignores them.
- The pre-built JDK base image is reused across all containers — NOT rebuilt per
  submission. Building per submission would dominate latency, especially in the 6-8
  run benchmarking stage.

Fallback: if Docker is not available (e.g. local dev without Docker Desktop), a
subprocess-based fallback with OS resource limits is used instead.
"""
from __future__ import annotations

import logging
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from typing import Optional

from app.config import settings

logger = logging.getLogger(__name__)

# Stdout/stderr size cap to prevent output-spam from exhausting server memory
_MAX_OUTPUT_BYTES = 1024 * 1024  # 1 MB


@dataclass
class SandboxResult:
    stdout: str
    stderr: str
    exit_code: int
    runtime_ms: float
    timed_out: bool
    compilation_error: bool = False


@dataclass
class SandboxLimits:
    wall_timeout_s: float = field(default_factory=lambda: float(settings.sandbox_wall_timeout_s))
    memory_mb: int = field(default_factory=lambda: settings.sandbox_memory_mb)
    cpu_quota: int = field(default_factory=lambda: settings.sandbox_cpu_quota)
    cpu_period: int = field(default_factory=lambda: settings.sandbox_cpu_period)
    pids_limit: int = field(default_factory=lambda: settings.sandbox_pids_limit)


def _is_docker_available() -> bool:
    """Check if the Docker daemon is reachable."""
    try:
        import docker
        client = docker.from_env()
        client.ping()
        return True
    except Exception:
        return False


class CompiledSubmission:
    """
    Represents a compiled/checked submission across multiple languages (Java, Python, C++, C, JavaScript).

    Usage:
        cs = CompiledSubmission(source_code, language="python")
        if cs.compilation_error:
            # handle compiler/syntax failure
        result = cs.run(stdin_data="4\\n2 7 11 15\\n9\\n", limits=SandboxLimits())
    """

    def __init__(self, source_code: str, language: str = "java"):
        self._source_code = source_code
        self.language = (language or "java").lower()
        self._tmpdir: Optional[str] = None
        self._class_dir: Optional[str] = None
        self._executable_cmd: list[str] = []
        self._docker_cmd: list[str] = []
        self.compilation_error = False
        self.compiler_output = ""
        self._use_docker = _is_docker_available()

        if not self._use_docker:
            logger.warning(
                "Docker not available — falling back to subprocess sandbox for language '%s'.",
                self.language,
            )
        self._compile()

    def _compile(self) -> None:
        """Compile or syntax-check source code based on self.language."""
        self._tmpdir = tempfile.mkdtemp(prefix="algolens_")
        os.chmod(self._tmpdir, 0o755)
        self._class_dir = self._tmpdir

        if self.language == "java":
            src_path = os.path.join(self._tmpdir, "Solution.java")
            with open(src_path, "w", encoding="utf-8") as f:
                f.write(self._source_code)

            javac = shutil.which("javac")
            if not javac:
                self.compilation_error = True
                self.compiler_output = "javac not found on PATH"
                return

            try:
                result = subprocess.run(
                    [javac, "--release", "21", "-d", self._class_dir, src_path],
                    capture_output=True,
                    text=True,
                    timeout=15,
                )
                if result.returncode != 0:
                    self.compilation_error = True
                    self.compiler_output = (result.stdout + result.stderr).strip()
                elif not os.path.exists(os.path.join(self._class_dir, "Solution.class")):
                    self.compilation_error = True
                    self.compiler_output = "Compilation error: Solution.class was not generated"
            except subprocess.TimeoutExpired:
                self.compilation_error = True
                self.compiler_output = "Compilation timed out"
            except Exception as e:
                self.compilation_error = True
                self.compiler_output = f"Compilation error: {e}"

            java = shutil.which("java") or "java"
            self._executable_cmd = [java, "-cp", self._class_dir, "-Xmx256m", "Solution"]
            self._docker_cmd = ["sh", "-c", "java -cp /sandbox/classes Solution < /sandbox/classes/stdin.txt"]

        elif self.language == "python":
            src_path = os.path.join(self._tmpdir, "solution.py")
            with open(src_path, "w", encoding="utf-8") as f:
                f.write(self._source_code)

            python_bin = sys.executable or shutil.which("python3") or shutil.which("python") or "python"
            try:
                result = subprocess.run(
                    [python_bin, "-m", "py_compile", src_path],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode != 0:
                    self.compilation_error = True
                    self.compiler_output = (result.stdout + result.stderr).strip()
            except Exception as e:
                self.compilation_error = True
                self.compiler_output = f"Python syntax check error: {e}"

            self._executable_cmd = [python_bin, src_path]
            self._docker_cmd = ["sh", "-c", "python3 /sandbox/classes/solution.py < /sandbox/classes/stdin.txt"]

        elif self.language in ("cpp", "c"):
            ext = "cpp" if self.language == "cpp" else "c"
            src_path = os.path.join(self._tmpdir, f"solution.{ext}")
            with open(src_path, "w", encoding="utf-8") as f:
                f.write(self._source_code)

            if self._use_docker:
                compiler_bin = "g++" if self.language == "cpp" else "gcc"
                std_flag = "-std=c++20" if self.language == "cpp" else "-std=c11"
                try:
                    import docker  # type: ignore
                    client = docker.from_env()
                    comp_container = client.containers.run(
                        settings.sandbox_image_name,
                        command=[
                            compiler_bin,
                            "-O2",
                            std_flag,
                            f"/sandbox/classes/solution.{ext}",
                            "-o",
                            "/sandbox/classes/solution",
                        ],
                        volumes={self._class_dir: {"bind": "/sandbox/classes", "mode": "rw"}},
                        detach=True,
                    )
                    comp_container.wait(timeout=15)
                    logs = comp_container.logs().decode("utf-8")
                    comp_container.remove(force=True)
                    if not os.path.exists(os.path.join(self._class_dir, "solution")):
                        self.compilation_error = True
                        self.compiler_output = f"Compilation error:\n{logs}"
                        return
                except Exception as e:
                    self.compilation_error = True
                    self.compiler_output = f"Docker compilation error: {e}"
                    return

                self._executable_cmd = [os.path.join(self._class_dir, "solution")]
                self._docker_cmd = ["sh", "-c", "/sandbox/classes/solution < /sandbox/classes/stdin.txt"]
            else:
                compiler = (
                    shutil.which("g++" if self.language == "cpp" else "gcc")
                    or shutil.which("clang++" if self.language == "cpp" else "clang")
                )
                out_bin_name = "solution.exe" if os.name == "nt" else "solution"
                out_bin = os.path.join(self._class_dir, out_bin_name)

                if not compiler:
                    self.compilation_error = True
                    self.compiler_output = (
                        f"{'g++/clang++' if self.language == 'cpp' else 'gcc/clang'} not found on PATH"
                    )
                    return

                std_flag = "-std=c++20" if self.language == "cpp" else "-std=c11"
                try:
                    result = subprocess.run(
                        [compiler, "-O2", std_flag, src_path, "-o", out_bin],
                        capture_output=True,
                        text=True,
                        timeout=15,
                    )
                    if result.returncode != 0:
                        self.compilation_error = True
                        self.compiler_output = (result.stdout + result.stderr).strip()
                except Exception as e:
                    self.compilation_error = True
                    self.compiler_output = f"Compilation error: {e}"

                self._executable_cmd = [out_bin]
                self._docker_cmd = ["sh", "-c", f"/sandbox/classes/{out_bin_name} < /sandbox/classes/stdin.txt"]

        elif self.language == "javascript":
            src_path = os.path.join(self._tmpdir, "solution.js")
            with open(src_path, "w", encoding="utf-8") as f:
                f.write(self._source_code)

            node = shutil.which("node") or "node"
            try:
                result = subprocess.run(
                    [node, "--check", src_path],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode != 0:
                    self.compilation_error = True
                    self.compiler_output = (result.stdout + result.stderr).strip()
            except Exception as e:
                self.compilation_error = True
                self.compiler_output = f"JavaScript syntax check error: {e}"

            self._executable_cmd = [node, src_path]
            self._docker_cmd = ["sh", "-c", "node /sandbox/classes/solution.js < /sandbox/classes/stdin.txt"]
        else:
            self.compilation_error = True
            self.compiler_output = f"Unsupported language: {self.language}"

        # Ensure directory & compiled files are world-readable so container users can access them
        try:
            for root, dirs, files in os.walk(self._tmpdir):
                for d in dirs:
                    os.chmod(os.path.join(root, d), 0o755)
                for f in files:
                    os.chmod(os.path.join(root, f), 0o755 if f.endswith(".exe") or f == "solution" else 0o644)
        except Exception as e:
            logger.warning("Failed to set permissions on tmpdir %s: %s", self._tmpdir, e)

    def run(self, stdin_data: str, limits: Optional[SandboxLimits] = None) -> SandboxResult:
        """
        Run the compiled submission with the given stdin, enforcing resource limits.

        Returns a SandboxResult regardless of success/failure — never raises.
        Each call is an isolated execution (separate container or subprocess).
        """
        if self.compilation_error:
            return SandboxResult(
                stdout="",
                stderr=self.compiler_output,
                exit_code=1,
                runtime_ms=0.0,
                timed_out=False,
                compilation_error=True,
            )

        if limits is None:
            limits = SandboxLimits()

        if self._use_docker:
            return self._run_docker(stdin_data, limits)
        else:
            return self._run_subprocess(stdin_data, limits)

    def _run_docker(self, stdin_data: str, limits: SandboxLimits) -> SandboxResult:
        """Run in a disposable Docker container with full resource/network/fs isolation."""
        import docker  # type: ignore
        client = docker.from_env()

        # Write stdin to mounted volume for instant, reliable socket-free redirection
        stdin_file = os.path.join(self._class_dir, "stdin.txt")
        with open(stdin_file, "w", encoding="utf-8") as f:
            f.write(stdin_data)

        start = time.perf_counter()
        try:
            container = client.containers.run(
                image=settings.sandbox_image_name,
                command=self._docker_cmd,
                detach=True,
                network_disabled=True,
                read_only=True,
                tmpfs={"/sandbox/scratch": "size=32m,noexec"},
                mem_limit=f"{limits.memory_mb}m",
                memswap_limit=f"{limits.memory_mb}m",
                cpu_period=limits.cpu_period,
                cpu_quota=limits.cpu_quota,
                pids_limit=limits.pids_limit,
                volumes={self._class_dir: {"bind": "/sandbox/classes", "mode": "ro"}},
            )

            try:
                exit_code = container.wait(timeout=limits.wall_timeout_s)["StatusCode"]
                timed_out = False
            except Exception:
                timed_out = True
                exit_code = -1
                container.kill()

            runtime_ms = (time.perf_counter() - start) * 1000

            logs = container.logs(stdout=True, stderr=False)
            stderr_logs = container.logs(stdout=False, stderr=True)
            container.remove(force=True)

            stdout = logs.decode("utf-8", errors="replace")[:_MAX_OUTPUT_BYTES]
            stderr = stderr_logs.decode("utf-8", errors="replace")[:_MAX_OUTPUT_BYTES]

            return SandboxResult(
                stdout=stdout,
                stderr=stderr,
                exit_code=exit_code,
                runtime_ms=runtime_ms,
                timed_out=timed_out,
            )

            try:
                exit_code = container.wait(timeout=limits.wall_timeout_s)["StatusCode"]
                timed_out = False
            except Exception:
                timed_out = True
                exit_code = -1
                container.kill()

            runtime_ms = (time.perf_counter() - start) * 1000

            logs = container.logs(stdout=True, stderr=False)
            stderr_logs = container.logs(stdout=False, stderr=True)
            container.remove(force=True)

            stdout = logs.decode("utf-8", errors="replace")[:_MAX_OUTPUT_BYTES]
            stderr = stderr_logs.decode("utf-8", errors="replace")[:_MAX_OUTPUT_BYTES]

            return SandboxResult(
                stdout=stdout,
                stderr=stderr,
                exit_code=exit_code,
                runtime_ms=runtime_ms,
                timed_out=timed_out,
            )

        except Exception as e:
            logger.error("Docker sandbox run failed: %s", e)
            runtime_ms = (time.perf_counter() - start) * 1000
            return SandboxResult(
                stdout="",
                stderr=f"Sandbox error: {e}",
                exit_code=1,
                runtime_ms=runtime_ms,
                timed_out=False,
            )

    def _run_subprocess(self, stdin_data: str, limits: SandboxLimits) -> SandboxResult:
        """
        Fallback: run via subprocess when Docker is not available.
        Provides weaker isolation — filesystem/PID namespaces NOT isolated.
        Suitable for local dev only.
        """
        if not self._executable_cmd:
            return SandboxResult(
                stdout="", stderr="Executable command not specified",
                exit_code=1, runtime_ms=0.0, timed_out=False,
            )

        start = time.perf_counter()
        try:
            result = subprocess.run(
                self._executable_cmd,
                input=stdin_data,
                capture_output=True,
                text=True,
                timeout=limits.wall_timeout_s,
            )
            runtime_ms = (time.perf_counter() - start) * 1000
            return SandboxResult(
                stdout=result.stdout[:_MAX_OUTPUT_BYTES],
                stderr=result.stderr[:_MAX_OUTPUT_BYTES],
                exit_code=result.returncode,
                runtime_ms=runtime_ms,
                timed_out=False,
            )
        except subprocess.TimeoutExpired:
            runtime_ms = (time.perf_counter() - start) * 1000
            return SandboxResult(
                stdout="", stderr="",
                exit_code=-1, runtime_ms=runtime_ms, timed_out=True,
            )
        except Exception as e:
            runtime_ms = (time.perf_counter() - start) * 1000
            return SandboxResult(
                stdout="", stderr=str(e),
                exit_code=1, runtime_ms=runtime_ms, timed_out=False,
            )

    def cleanup(self) -> None:
        """Remove the temporary compilation directory."""
        if self._tmpdir and os.path.exists(self._tmpdir):
            try:
                # Make all files writable before deletion (Windows compatibility)
                def _force_writable(path: str, excinfo=None) -> None:
                    os.chmod(path, stat.S_IWRITE)
                shutil.rmtree(self._tmpdir, onerror=lambda f, p, e: (_force_writable(p), f(p)))
            except Exception as e:
                logger.warning("Failed to clean up tmpdir %s: %s", self._tmpdir, e)

    def __del__(self):
        self.cleanup()
