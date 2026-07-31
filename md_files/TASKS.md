# AlgoLens — Tasks

Status legend: `[x]` done · `[~]` in progress · `[ ]` not started

## Phase 1 — Core Backend Pipeline

- [x] Project skeleton (FastAPI app, modular structure)
- [x] Auth module: register, login, refresh, password hashing, JWT access/refresh tokens
- [x] Sandbox executor (`CompiledSubmission`): compile-once-run-many, OS resource limits, Java Security Manager policy
- [x] Problem data module: generator registry + Two Sum reference problem
- [x] Correctness service: comparator types (exact / numeric_tolerance / sorted)
- [x] Benchmark service: scaled-input runner with warm-up discard and median timing
- [x] Complexity classifier: log-log regression, O(n) vs O(n log n) disambiguation, confidence score
- [x] Structural hint engine: regex/token-based pattern detection (nested loop, unmemoized recursion)
- [x] Pipeline orchestration service tying the above together
- [x] Routers: `/problems`, `/submissions` (async via BackgroundTasks)
- [x] Seed script + smoke test (register → submit brute-force Two Sum → classified as O(n²) with hint)

## Phase 2 — Problem Bank + Sandbox Hardening

- [x] Expand problem bank to 8–10 problems (Contains Duplicate, LCP, Valid Anagram, Container With Most Water, Kadane's, Climbing Stairs, Binary Search, Merge Intervals)
- [x] Sandbox robustness test suite (infinite loop, memory bomb, fork bomb, output spam, file-write escape, network escape attempts)
- [x] Per-user rate limiting on `POST /submissions`

## Phase 3 — Observability + Missing Endpoints + Test Coverage

- [x] `GET /users/{id}/history` endpoint
- [x] Structured pipeline logging (rotating file handler, stage-transition logs)
- [x] Unit tests: complexity classifier against synthetic known-slope data
- [x] Unit tests: correctness comparators (table-driven)
- [x] Integration test: full pipeline across correct / inefficient / wrong / non-compiling submissions

## Phase 4 — Deployment Prep (original SSH-only plan — superseded, kept as fallback)

- [x] `scripts/probe_server.sh` — checks systemd/cron/JDK/Python/port availability on the target server
- [x] Tier 1 deployment scripts (raw nohup + PID file: run/stop/status/restart)
- [x] Tier 2 — crontab watchdog (if cron available, no systemd)
- [x] Tier 3 — systemd `--user` unit template (if available)
- [x] ~~Actually run `probe_server.sh` against the real college server~~ — superseded: Docker + root confirmed available, see Phase 4b

## Phase 4b — Docker Migration (current deployment path)

- [x] Migrate sandbox from subprocess + resource limits + Java Security Manager to Docker container-based isolation (see `SECURITY.md`)
- [x] Write `docker-compose.yml` (api, db, frontend, pre-built sandbox base image)
- [x] Update `DATABASE.md` / `.env` config to use Postgres via the `db` Compose service instead of SQLite in production
- [ ] Re-run `tests/test_sandbox_robustness.py` against the new Docker-based sandbox — confirm same expected-failure-mode results as the original design
- [ ] First real deployment to college server via `docker compose up -d`
- [ ] Confirm sandbox base image is reused across submissions/benchmark runs, not rebuilt per run (latency check)

## Phase 5 — Correctness Checking Bug Fix

- [x] Root-cause investigation: why empty/wrong submissions were passing
- [x] Fix applied at the actual source (not a special-cased patch)
- [x] Verdict states properly distinguished: Accepted / Wrong Answer / Compilation Error / Runtime Error / Time Limit Exceeded
- [x] Regression tests for all six scenarios (empty, wrong class name, wrong answer, runtime exception, correct, zero test cases loaded)

## Phase 6 — Frontend

- [x] Design plan (Pass 1): palette, typography, layout, signature element — orange-accent theme
- [x] Problem list screen
- [x] Problem detail + code editor screen (Monaco)
- [x] Results screen: verdict banner, test case results panel, complexity comparison chart, structural hint
- [x] Submission history screen
- [x] Retheme: dark blue → orange accent palette, applied consistently across all screens
- [x] LeetCode-style elements: difficulty tags, verdict banner, test-case results panel
- [x] Landing page (public, same palette, real data for problem-bank preview)
- [x] Auth-gated routing: Problems and related routes require login, with redirect-back-after-login
- [x] Session persistence across refresh (token storage + silent refresh)
- [ ] Run/Submit distinction (deferred — needs sample-vs-hidden test case split in backend data)
- [ ] Acceptance-rate stat on problem list (deferred — needs backend tracking, not faked)

## Phase 7 — Documentation

- [x] Capstone project report (docx)
- [x] System Design document (docx + markdown)
- [x] Project Scope document (docx, with ERD + Use Case diagram)
- [x] This documentation set (`README.md` through `AI_CONTEXT.md`)

## Backlog / Future Work (not scheduled)

- [ ] Multi-language submission support (Python, C++)
- [ ] Space-complexity measurement
- [ ] Full AST-based Java parsing for structural hints (replacing regex heuristics)
- [ ] ML-based complexity classification (replacing/augmenting log-log regression)
- [ ] LLM-generated, code-specific inefficiency explanations
- [ ] Community-contributed problems with moderation workflow
- [ ] Personalized practice recommendations based on submission history
- [ ] Jenkins CI/CD pipeline
- [ ] True containerized sandboxing (Docker/gVisor) if root access ever becomes available
