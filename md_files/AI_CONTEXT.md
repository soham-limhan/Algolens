# AlgoLens — Context for AI Assistants

This file is for AI coding assistants (Antigravity, Claude, or others) working on this repository. Read this before making changes — it captures constraints and conventions that aren't always obvious from the code alone.

## What This Project Actually Is

AlgoLens is a **competitive coding platform** — same category as LeetCode — with one added feature: after a solution is judged, it shows how the submission's measured time complexity compares to the optimal complexity for that problem. Treat it as a coding judge first. Do not drift the framing back toward a "lab" or "graded exam" metaphor — that direction was explicitly tried and reverted (see `CHANGELOG.md` 0.5.0).

## Hard Constraints — Do Not Violate Without Explicit Instruction

- **Docker + root are now available on the college deployment server** (environment changed from the original SSH-only, non-root assumption). The sandbox and deployment have both been migrated to use Docker as the primary mechanism — see `SECURITY.md` and `DEPLOYMENT.md`. Do not revert to the old subprocess + `resource.setrlimit` + Java Security Manager sandbox design as the primary path; that design is retained only as a documented fallback in case Docker access is ever lost. If working from an older summary or an out-of-date prompt that still says "no Docker," this file and the dated entries in `CHANGELOG.md` are the source of truth — check the changelog before assuming an old constraint still holds.
- **No Jenkinsfile/CI pipeline** unless explicitly requested — it's a deliberately separate, later phase. (Note: Jenkins can now build/push Docker images or trigger `docker compose up -d --build` remotely, which simplifies that phase whenever it happens — but don't build it preemptively.)
- **Java only** for submissions in v1 — do not add multi-language support speculatively, even though Docker makes it more tractable than before.
- **In-process background tasks** (FastAPI `BackgroundTasks`), not a new job-queue dependency (Celery/Redis), unless explicitly asked to add one — this constraint is unrelated to the Docker change and still holds.
- **PostgreSQL, not SQLite, for anything deployment-related** now that Postgres runs easily as a Docker Compose service — SQLite remains fine for fast local dev iteration only.

## Design Invariants — Preserve These

- **Correctness must gate benchmarking.** A submission only proceeds to complexity benchmarking after passing all fixed test cases. If touching the pipeline, verify this invariant still holds (assert zero `BenchmarkRun` rows for failing submissions) rather than assuming it does.
- **The sandbox is one primitive, reused for two purposes.** Correctness checking and benchmarking both use `CompiledSubmission` — don't build a second, separate execution path for one of them.
- **Structural hints only run when there's a complexity gap.** This is an efficiency choice (skip unnecessary pattern-matching work), not a technical dependency — don't remove the gate.
- **Problem generator logic lives in code (`app/problems_data/`), never in the database as data or eval-able strings.** See `DATABASE.md` Section 3 for the full rationale — this is a deliberate security/architecture decision, not an oversight to "simplify."
- **Verdicts are specific, not a boolean.** Accepted / Wrong Answer / Compilation Error / Runtime Error / Time Limit Exceeded are distinct states carrying distinct information. Don't collapse them into a generic pass/fail — this exact collapse caused the bug fixed in `CHANGELOG.md` 0.4.1.

## When Fixing Bugs

**Investigate and report the root cause before fixing.** Do not patch around a reported symptom with a special case. If a bug report says "X does the wrong thing," trace through the actual code path first: is data loading correctly? Is a comparison/aggregation function logically correct (e.g., `all()` vs `any()`, correct default on empty input)? Is an exception being silently swallowed by a broad `except: pass`? Is the frontend rendering from real API state or an assumed/optimistic one? Report findings before applying a fix. See `CHANGELOG.md` 0.4.1 for the model case: the reported symptom was "empty submissions pass," but the actual bug was general enough that wrong-but-non-empty answers were likely also passing — fixing only the empty-input case would have left the more serious bug in place.

## When Building New Features

- State assumptions explicitly and proceed with a reasonable default rather than stalling on ambiguity, **except** for deployment-environment facts that are genuinely unknown — for those, build a diagnostic step first rather than guessing (see `scripts/probe_server.sh` as the model; it's less critical now that Docker + root are confirmed available, but the same "verify, don't assume" principle still applies to anything about the deployment environment that hasn't been explicitly confirmed).
- Don't fabricate data to make a UI look complete. If a stat (e.g. acceptance rate) isn't tracked by the backend yet, flag it as a needed backend addition rather than hardcoding a placeholder number into the UI.
- Update the relevant doc file(s) alongside the code change — `API.md` for endpoint changes, `DATABASE.md` for schema changes, `UI_UX.md` for new screens/states, `TASKS.md` always.

## Design Language

- Avoid the generic AI-generated-UI defaults explicitly ruled out in `UI_UX.md`: warm cream + terracotta, near-black + neon, broadsheet/hairline-rule layouts. The current theme is an orange accent, chosen deliberately — don't drift back toward these defaults in future UI work.
- Copy is written from the learner's side of the screen — no backend vocabulary ("pipeline," "job," "empirical classifier") in user-facing text.

## Testing Expectations

- Every bug fix needs a regression test that fails on the pre-fix code.
- Sandbox-related tests must assert the **specific expected failure mode** (timeout vs. resource-limit kill vs. security exception), not a generic "did not succeed" — see `TESTING.md` Section 5 for why.
- Integration tests that compile/run real Java are slow and marked `@pytest.mark.integration`, kept separate from the fast unit suite.

## Prompt-Writing Conventions (for build prompts written by/for AI agents)

When writing a build prompt for this project:
- State hard constraints up front (this file's list above).
- Include explicit non-goals for the current phase, to prevent scope creep into adjacent work not yet ready.
- For anything environment-dependent and unconfirmed, prefer "build a diagnostic step first" over guessing.
- Request a deliverable that includes a short written summary of what was actually done vs. deferred, so `TASKS.md` and `CHANGELOG.md` can be updated accurately.
