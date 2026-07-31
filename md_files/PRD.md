# AlgoLens — Product Requirements Document

## 1. Problem Statement

Existing coding-practice platforms (LeetCode, HackerRank, and similar) evaluate submissions almost entirely on correctness. A learner can pass hundreds of problems using brute-force approaches and never be told their solution is inefficient, because these platforms don't measure or compare complexity. The most transferable interview skill — reasoning about time/space complexity — has no feedback loop in existing tools.

## 2. Goal

Build a platform that judges submitted code like a standard online judge, **and** empirically measures the submission's time complexity, compares it to the problem's known optimum, and gives a targeted structural hint when there's a gap — without revealing the optimal solution's code.

## 3. Target User

A student preparing for technical interviews who already practices algorithmic problems and wants feedback on *efficiency*, not just correctness. Primary persona: the project author's own use case (practicing LeetCode-style problems, MCA capstone context).

## 4. Scope

### In scope (v1)
- Java submissions only.
- A curated problem bank (8–10 problems at launch) with well-defined optimal complexities.
- Standard judge verdicts: Accepted, Wrong Answer, Compilation Error, Runtime Error, Time Limit Exceeded.
- Empirical time-complexity classification (not space complexity).
- Structural hints via lightweight pattern detection (regex/token-based, not full AST parsing).
- JWT-based auth, submission history.
- Deployment on an SSH-only, non-root college server (no Docker in the initial deployment path).

### Out of scope (v1)
- Multi-language support (Python/C++/JS submissions).
- Space-complexity measurement.
- Community-contributed problems / moderation workflow.
- Full AST-based Java parsing for hints.
- Plagiarism/academic-integrity detection between users.
- Production-grade job queue (Celery/Redis) — in-process background tasks are sufficient at this scale.
- Real-time interview simulation mode.

See [`ARCHITECTURE.md`](./ARCHITECTURE.md) Future Work section for what's deliberately deferred.

## 5. Functional Requirements

| ID | Requirement |
|---|---|
| FR-1 | A learner can register and log in. |
| FR-2 | A learner can browse a bank of algorithmic problems with title and difficulty. |
| FR-3 | A learner can submit Java code for a chosen problem via an in-browser editor. |
| FR-4 | The system verifies correctness against fixed test cases before anything else runs. |
| FR-5 | A failing submission returns a specific verdict (Wrong Answer / Compilation Error / Runtime Error / Time Limit Exceeded) with detail on what failed. |
| FR-6 | On a correct (Accepted) submission, the system benchmarks it against scaled input sizes and classifies its empirical time complexity. |
| FR-7 | The system compares empirical complexity to the problem's known optimum and shows both, visually, on a shared curve. |
| FR-8 | When a gap exists, the system shows a structural hint explaining what pattern to reconsider — never the optimal solution's code. |
| FR-9 | A learner can view their submission history (verdict + complexity per attempt). |
| FR-10 | Submission is asynchronous — the client polls for status rather than blocking on a long-running request. |

## 6. Non-Functional Requirements

- **Isolation**: no submission may affect the host, other submissions, or other users.
- **Bounded latency**: full pipeline for one submission should complete within a fixed budget.
- **Availability**: a pathological submission must not degrade service for others.
- **Reproducibility**: repeated benchmarking of the same code should yield a consistent classification, backed by an explicit confidence score.
- **Deployability without root**: the system must run correctly on a server where only SSH access is available — no Docker, no sudo.

## 7. Success Criteria

- A brute-force and an optimal solution to the same problem, both correct, are visibly and correctly distinguished by complexity classification in a live demo.
- The sandbox survives adversarial submissions (infinite loops, fork bombs, memory bombs) without crashing the service — verified by the sandbox robustness test suite.
- End-to-end flow (register → submit → judge → classify → hint) works on the deployed college-server instance, not just locally.

## 8. Open Questions / Risks

- Empirical complexity classification is inherently noisy (hardware, JIT warm-up, GC pauses) — see `ARCHITECTURE.md` Limitations.
- Regex-based structural hints can false-positive on code that's structurally similar to a known inefficiency but contextually necessary.
- College server capabilities (systemd/cron availability, existing reverse proxy) were unconfirmed at time of writing — see `DEPLOYMENT.md`.
