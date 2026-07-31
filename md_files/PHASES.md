# AlgoLens — Build Phases

This file sequences the whole project into ordered, self-contained phases — each one buildable (and promptable to an AI coding agent) on its own, with clear inputs, outputs, and exit criteria. Work top to bottom; don't start a phase until the one(s) it depends on are actually done, not just "mostly done."

Cross-references: `TASKS.md` tracks fine-grained checklist items within each phase; this file is the higher-level sequencing. `AI_CONTEXT.md` has standing rules that apply across every phase (investigate before fixing, no fabricated data, don't reintroduce old constraints).

**Environment note**: Docker + root are available on the deployment server. Phases below assume Docker-based sandboxing and deployment from the start — this is not the original SSH-only plan.

---

## Phase 0 — Project Setup

**Goal**: a running skeleton, nothing functional yet.

- Repository structure per `ARCHITECTURE.md` Section 3.
- `backend/requirements.txt`, `.env.example`.
- `app/config.py` (env-based settings via pydantic-settings).
- `app/db/database.py` (SQLAlchemy engine/session/Base, `DATABASE_URL`-driven).
- `app/main.py` — FastAPI app object, `/health` endpoint, CORS middleware.
- `docker-compose.yml` skeleton (services stubbed, not yet functional): `api`, `db`.

**Depends on**: nothing.

**Exit criteria**: `docker compose up -d` (or local `uvicorn`) serves `GET /health` → `{"status": "ok"}`.

---

## Phase 1 — Database Models

**Goal**: the schema exists and matches `DATABASE.md`.

- `app/models/`: `User`, `Problem`, `TestCase`, `InefficiencySignature`, `Submission`, `BenchmarkRun`.
- UUID string primary keys, explicit foreign keys, relationships both directions where used.
- `Base.metadata.create_all()` wired into app startup.

**Depends on**: Phase 0.

**Exit criteria**: tables actually create correctly against both SQLite (local dev) and Postgres (via the `db` Compose service) without code changes — only `DATABASE_URL` differs.

---

## Phase 2 — Auth Module

**Goal**: register/login/refresh work end-to-end, tokens are real JWTs, passwords are hashed.

- `app/auth/security.py` — bcrypt hashing, access/refresh JWT creation and decoding with type-checking.
- `app/auth/dependencies.py` — `get_current_user`.
- `app/auth/router.py` — `/auth/register`, `/auth/login`, `/auth/refresh` (with rotation).
- `app/schemas/auth.py`.

**Depends on**: Phase 1 (`User` model).

**Exit criteria**: register → login → hit a token-protected dummy route → refresh → hit it again with the new token. Duplicate-email registration correctly rejected. Wrong password gives the same error message as a nonexistent email.

---

## Phase 3 — Docker Sandbox Module

**Goal**: untrusted Java code can be compiled and run safely, in a disposable container, with all resource/network/filesystem controls actually enforced — this is the highest-risk module in the whole project and should be proven before anything else depends on it.

- `app/sandbox/executor.py` — `CompiledSubmission` class: compile once (in a build step or an ephemeral container), then `.run(stdin_data, limits)` many times against fresh disposable containers per run.
- Container config: `network_disabled=True`, `read_only=True` root filesystem with a small writable `tmpfs`, `mem_limit`/`memswap_limit`, `cpu_period`/`cpu_quota`, `pids_limit`, host-side wall-clock timeout via `wait(timeout=...)` + force-kill/remove.
- A pre-built JDK 21 base image, built once, reused across runs (not rebuilt per submission).
- `tests/test_sandbox_robustness.py` — the adversarial suite from `TESTING.md` Section 5, asserting the **specific** expected failure mode per hostile case (timeout / cgroup memory kill / `pids_limit` / filesystem-write blocked / network blocked), not a generic pass/fail.

**Depends on**: Phase 0 (Docker Compose skeleton needs to actually run containers, not just stub services).

**Exit criteria**: the full sandbox robustness suite passes, with each hostile case's failure mode explicitly verified. A normal, well-behaved submission run interleaved between hostile ones is completely unaffected (proves per-run isolation and cleanup, not just that limits fire once).

---

## Phase 4 — Problem Data & Seed

**Goal**: the problem bank exists as code + data, per the storage split in `DATABASE.md` Section 3.

- `app/problems_data/registry.py` + one generator module per problem (`generate(n, seed) -> str`).
- `app/seed.py` — idempotent, populates `Problem` + `TestCase` + `InefficiencySignature` rows.
- Two Sum as the first reference problem (3+ test cases including an edge case, one `nested_loop_lookup` signature with real hint text).

**Depends on**: Phase 1 (models), Phase 3 (sandbox — needed to manually verify a reference solution actually runs correctly before trusting the seeded test cases).

**Exit criteria**: `python -m app.seed` runs cleanly and is safe to re-run without duplicating data.

---

## Phase 5 — Correctness Service

**Goal**: a submission gets a real, specific verdict against fixed test cases.

- `app/services/correctness.py` — comparator dispatch (`exact`, `numeric_tolerance`, `sorted`), `run_correctness_check`.
- Verdicts distinguished: Accepted / Wrong Answer / Compilation Error / Runtime Error / Time Limit Exceeded — not a boolean.
- `tests/test_correctness_comparators.py` — table-driven per comparator type.

**Depends on**: Phase 3 (sandbox), Phase 4 (seeded test cases to check against).

**Exit criteria**: a correct submission, a wrong-answer submission, a non-compiling submission, and a runtime-exception submission each get the *correct, distinct* verdict — verified explicitly, not just "did not crash." This is the exact class of bug that caused the correctness-checking regression in project history (see `CHANGELOG.md` 0.4.1) — test for it deliberately here, don't assume it away.

---

## Phase 6 — Benchmark Service

**Goal**: a correct submission can be run against scaled inputs and timed reliably.

- `app/services/benchmark.py` — scaled-input loop, per-repetition re-randomized input, warm-up-run discard, median timing, timeout budget that scales with input size, early-stop on repeated timeout.

**Depends on**: Phase 3 (sandbox), Phase 4 (generators).

**Exit criteria**: running the same correct submission twice produces reasonably consistent runtime curves (allowing for real-world noise); a clearly-O(n²) brute-force submission and a clearly-O(n) optimal submission produce visibly different curve shapes.

---

## Phase 7 — Complexity Classifier

**Goal**: a runtime curve gets classified into a standard Big-O label with a confidence score.

- `app/services/complexity.py` — log-log linear regression, slope-to-class mapping, O(n) vs O(n log n) disambiguation, `is_gap()` ordinal comparison against a problem's optimum.
- `tests/test_complexity_classifier.py` — synthetic known-slope data per `TESTING.md` Section 2.

**Depends on**: Phase 6 (produces the input this consumes) — but can be developed and unit-tested against synthetic data independently, in parallel with Phase 6 if useful.

**Exit criteria**: all synthetic-data unit tests pass, including the insufficient-data and all-timed-out edge cases returning graceful results rather than exceptions.

---

## Phase 8 — Structural Hint Engine

**Goal**: a genuine complexity gap produces a specific, useful hint — not a generic message.

- `app/services/hints.py` — regex/token-based detectors (`nested_loop_lookup`, `unmemoized_recursion`), matched against a problem's stored `InefficiencySignature` rows.

**Depends on**: Phase 4 (signature data), Phase 7 (gap detection is the trigger condition).

**Exit criteria**: the seeded Two Sum brute-force reference solution triggers the `nested_loop_lookup` hint; a proper HashMap-based solution does not trigger any hint.

---

## Phase 9 — Pipeline Orchestration

**Goal**: everything above is wired into one coherent flow with correct status transitions.

- `app/services/pipeline.py` — compile → correctness (gate) → benchmark → classify → hint (conditional) → persist, with `Submission.status` transitions logged at each stage.
- Structured, rotating-file logging per `DEPLOYMENT.md`.

**Depends on**: Phases 3–8, all of them.

**Exit criteria**: `tests/test_submission_pipeline_integration.py` (all six scenarios from `TESTING.md` Section 4) passes, including the explicit assertion that a failing submission produces **zero** `BenchmarkRun` rows.

---

## Phase 10 — API Routers

**Goal**: the pipeline is reachable over HTTP, asynchronously, correctly scoped per user.

- `app/routers/problems.py`, `app/routers/submissions.py` (async via `BackgroundTasks`, own DB session per background task).
- `GET /users/{id}/history`, paginated, access-controlled.
- Per-user rate limiting on `POST /submissions`.

**Depends on**: Phase 9, Phase 2 (auth-gating the routes).

**Exit criteria**: full manual smoke test from `TESTING.md` Section 7 passes against the running API — including the empty-submission regression check.

---

## Phase 11 — Frontend Design System

**Goal**: a deliberate visual identity exists before any screen is built against it.

- Palette (orange accent + semantic verdict colors + difficulty-tag colors, kept visually distinct from each other), typography roles, component conventions — per `UI_UX.md`.
- Explicit self-critique against the three generic-AI-UI defaults ruled out in `UI_UX.md`.

**Depends on**: nothing technical — can start in parallel with backend phases, but should finish before Phase 12.

**Exit criteria**: named hex values and typography choices recorded in `UI_UX.md` (replacing the `[hex]` placeholders), reviewed before component work starts.

---

## Phase 12 — Frontend Core Screens

**Goal**: problem list, editor, results, and history screens exist and work against the real API.

- Problem list (quiet, secondary).
- Problem detail + Monaco editor + submit action.
- Results screen: verdict banner, test-case results panel, complexity comparison chart, structural hint — in that visual order.
- Submission history.

**Depends on**: Phase 10 (real API to build against), Phase 11 (design system to build with).

**Exit criteria**: a full user journey (submit brute-force → see O(n²) + hint → submit optimal → see O(n) + no hint) works end-to-end in the browser.

---

## Phase 13 — Landing Page + Auth Gating

**Goal**: a public entry point exists, and protected routes actually require login.

- Landing page (same palette, real `GET /problems` data for the preview, no fabricated stats).
- Route guards on Problems/detail/results/history, redirect-to-login, redirect-back-after-login.
- Session persistence (silent refresh via `/auth/refresh`), documented token-storage tradeoff in `SECURITY.md`.

**Depends on**: Phase 12.

**Exit criteria**: logged-out → click Problems → redirected to login → log in → land back on Problems (not a generic dashboard). Page refresh does not silently log the user out.

---

## Phase 14 — Docker Compose Deployment

**Goal**: the whole system runs on the college server via `docker compose up -d`.

- `docker-compose.yml` finalized: `api`, `db` (Postgres), `frontend`, sandbox base image.
- `.env` with real secrets (never committed).
- Seed run against the real deployment database.

**Depends on**: Phase 9 (backend functionally complete), Phase 13 (frontend functionally complete), Phase 3 (sandbox already proven in isolation, but re-verify on the actual server hardware here).

**Exit criteria**: `DEPLOYMENT.md` Section 8 checklist fully checked off, including re-running the sandbox robustness suite against the deployed instance.

---

## Phase 15 — Jenkins CI/CD

**Goal**: build/test/deploy is automated, not manual.

- Jenkinsfile: run unit + integration + sandbox robustness tests, build Docker images, deploy (or trigger deployment) on success.

**Depends on**: Phase 14 (a manually-working deployment to automate).

**Exit criteria**: a pushed commit triggers a Jenkins build that runs the full test suite and, on success, produces a deployable image/deployment — not scoped further here; write a dedicated `CI_CD.md` when this phase starts if more detail is needed.

---

## Phase 16 — Documentation Finalization

**Goal**: all docs reflect what was actually built, not what was planned.

- Reconcile `TASKS.md`, `CHANGELOG.md` against actual completed work.
- Fill in any remaining placeholders (palette hex values, token-storage decision, team member details in the capstone report).
- Final pass on `AI_CONTEXT.md` to remove any now-stale constraints.

**Depends on**: everything else.

**Exit criteria**: a new contributor (or AI agent) could read the docs alone and understand the system without needing this conversation history.

---

## Phase Status Tracker

| Phase | Name | Status |
|---|---|---|
| 0 | Project Setup | ☐ |
| 1 | Database Models | ☐ |
| 2 | Auth Module | ☐ |
| 3 | Docker Sandbox Module | ☐ |
| 4 | Problem Data & Seed | ☐ |
| 5 | Correctness Service | ☐ |
| 6 | Benchmark Service | ☐ |
| 7 | Complexity Classifier | ☐ |
| 8 | Structural Hint Engine | ☐ |
| 9 | Pipeline Orchestration | ☐ |
| 10 | API Routers | ☐ |
| 11 | Frontend Design System | ☐ |
| 12 | Frontend Core Screens | ☐ |
| 13 | Landing Page + Auth Gating | ☐ |
| 14 | Docker Compose Deployment | ☐ |
| 15 | Jenkins CI/CD | ☐ |
| 16 | Documentation Finalization | ☐ |

Mark ☐ → ☑ as each phase's exit criteria are actually met — not when work "starts," and not based on an AI agent's own claim of completion without the exit criteria being independently verified (run the tests, run the smoke test).
