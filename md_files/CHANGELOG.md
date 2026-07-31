# Changelog

All notable changes to AlgoLens are documented here. Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Planned
- First real deployment to college server via `docker compose up -d`.
- Re-run sandbox robustness suite against the new Docker-based sandbox to confirm parity with the original design's expected failure modes.
- Run/Submit distinction on the frontend (pending backend sample-vs-hidden test case data).
- Jenkins CI/CD pipeline (now simplified — can build/push images or trigger `docker compose up -d --build` remotely).

## [0.6.0] — Environment Change: Docker + Root Now Available

### Changed
- **Environment**: Docker and root/sudo access confirmed available on the college deployment server (originally SSH-only, non-root). This is a deployment-environment change, not a design preference — documented explicitly since it reverses an earlier hard constraint.
- **Sandbox**: migrated from subprocess + `resource.setrlimit` + Java Security Manager to real Docker container-based isolation (filesystem and PID namespaces now actually isolated, not just resource-capped). Original design retained as a documented fallback in `SECURITY.md`.
- **Deployment**: migrated from the three-tier nohup/cron/systemd approach to Docker Compose (`api`, `db`, `frontend`, sandbox base image services). Original tiered scripts retained in `scripts/deploy/` as a fallback, no longer the primary path.
- **Database**: production now uses PostgreSQL via a Docker Compose service, rather than SQLite (which was the default specifically because Postgres wasn't reliably installable without sudo).

### Updated documentation
- `SECURITY.md`, `DEPLOYMENT.md`, `ARCHITECTURE.md`, `DATABASE.md`, `README.md`, `AI_CONTEXT.md`, `TASKS.md` all updated to reflect the new environment. `AI_CONTEXT.md`'s hard-constraints list flipped from "no Docker" to "Docker + root available" to prevent future AI-assisted work from reverting to the old assumption.

## [0.5.0] — Frontend Retheme + Landing Page + Auth Gating

### Changed
- Removed the initial dark-blue theme in favor of an orange-accent palette, applied consistently across all screens.
- Reframed the product from a "lab / annotated exam" visual identity to a standard competitive-coding-platform feel, closer to LeetCode's own conventions.

### Added
- LeetCode-style elements: difficulty tags, verdict banner, test-case results panel styled per verdict.
- Public landing page (same palette, real problem-bank data for the preview section, no fabricated stats).
- Auth-gating on Problems and related routes, with redirect-back-after-login and session persistence across page refresh via silent token refresh.

## [0.4.1] — Correctness Checking Bug Fix

### Fixed
- **Root cause**: submissions with empty/invalid source (and potentially wrong-but-non-empty answers) were being marked as passing instead of failing. Investigated before patching — traced to the comparator/verdict aggregation logic and test-case loading path rather than special-casing the empty-input symptom.
- Verdicts now properly distinguished: Accepted / Wrong Answer / Compilation Error / Runtime Error / Time Limit Exceeded (previously collapsed into an under-specified pass/fail).
- Benchmarking and complexity classification now verified to only trigger on a genuine Accepted verdict.

### Added
- Regression tests: empty submission, wrong class name, always-wrong-answer submission, runtime exception, correct submission, and zero-test-cases-loaded edge case — all assert the correct verdict rather than a generic pass/fail.

## [0.4.0] — Initial Frontend Design

### Added
- Design plan and Pass 1 self-critique against generic-AI-UI defaults.
- Problem list, problem detail/editor, results, and history screens (initial dark-themed version, later retheme d in 0.5.0).

## [0.3.0] — Deployment Prep

### Added
- `scripts/probe_server.sh` — read-only diagnostic script to determine systemd/cron availability, JDK/Python versions, port availability, and proxy presence on the target server before committing to a deployment approach.
- Three-tier deployment scripts, all sharing the same app entrypoint:
  - Tier 1: raw `nohup` + PID-file-based run/stop/status/restart.
  - Tier 2: crontab watchdog with lock-file protection against overlapping runs.
  - Tier 3: `systemd --user` unit template, with notes on the `loginctl enable-linger` requirement.

## [0.2.0] — Observability + Missing Endpoint + Test Coverage

### Added
- `GET /users/{id}/history` endpoint (was specified in the original System Design doc but not implemented in the initial build).
- Structured, rotating-file pipeline logging (stage transitions, elapsed time, sandbox run durations).
- Unit tests: complexity classifier against synthetic known-slope data; correctness comparators (table-driven).
- Integration test suite covering correct/inefficient/wrong/non-compiling submissions end-to-end, plus history access control between two different users.

## [0.1.1] — Sandbox Hardening + Problem Bank Expansion

### Added
- Expanded problem bank from 1 to 8–10 problems (Contains Duplicate, Longest Common Prefix, Valid Anagram, Container With Most Water, Maximum Subarray, Climbing Stairs, Binary Search, Merge Intervals), each with generator, test cases, and at least one inefficiency signature.
- `tests/test_sandbox_robustness.py` — adversarial submissions (infinite loop, memory bomb, fork/thread bomb, output spam, file-write escape attempt, network access attempt) with assertions on the *specific* expected failure mode, not just "did not succeed."
- Per-user rate limiting on `POST /submissions`.

## [0.1.0] — Initial Backend Pipeline

### Added
- Project skeleton, modular backend structure (`auth/`, `sandbox/`, `problems_data/`, `services/`, `routers/`).
- Auth module: registration, login, JWT access/refresh tokens with rotation.
- Sandbox executor (`CompiledSubmission`): compile-once-run-many design, OS resource limits (`RLIMIT_CPU`, `RLIMIT_AS`, `RLIMIT_NPROC`, `RLIMIT_FSIZE`), Java Security Manager deny-by-default policy — built without Docker, for an SSH-only, non-root deployment target.
- Correctness service with pluggable comparators (exact / numeric_tolerance / sorted).
- Benchmark service: scaled-input runner with warm-up-run discard and median timing.
- Complexity classifier: log-log linear regression, O(n) vs O(n log n) disambiguation via runtime/n correlation with log(n), R²-derived confidence score.
- Structural hint engine (regex/token-based pattern detection: nested-loop-lookup, unmemoized recursion).
- Pipeline orchestration service tying correctness → benchmarking → classification → hints together, with status transitions persisted at each stage.
- Two Sum as the first seeded reference problem.
- Smoke test: register → login → submit brute-force Two Sum → correctly classified as O(n²).

## [0.0.1] — Project Planning

### Added
- Capstone project report and System Design document.
- Project scope document with ERD and use case diagram.
- Decision to scope AlgoLens as complexity-aware competitive coding platform, differentiated from a plagiarism-detection or generic full-stack project idea considered earlier.
