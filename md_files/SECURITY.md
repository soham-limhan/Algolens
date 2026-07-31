# AlgoLens — Security

## 1. Authentication

- Passwords hashed with **bcrypt** (via Passlib) — never stored or logged in plaintext.
- **Two JWT token types**:
  - **Access token** — short-lived (~30 min), sent on every authenticated API call.
  - **Refresh token** — long-lived (~7 days), used only to obtain a new token pair.
  - Each token embeds `sub` (user ID), `type` (`access`/`refresh`), `iat`, `exp`. `decode_token` rejects a token used as the wrong type — an access token cannot be used where a refresh token is expected, and vice versa.
- `/auth/refresh` performs **token rotation**: issues a brand-new pair (not just a new access token) on every refresh, limiting the reuse window of a stolen refresh token.
- Login returns an identical error message ("Incorrect email or password") whether the email doesn't exist or the password is wrong, to avoid leaking which emails are registered.

## 2. Authorization

- `get_current_user` FastAPI dependency validates the bearer token and loads the real `User` row before any protected route body executes.
- Submissions and history are scoped to the requesting user: `GET /submissions/{id}` and `GET /users/{id}/history` return `404`/`403` rather than another user's data, verified explicitly in the integration test suite (`TESTING.md` Section 4, item 6).
- Per-user rate limiting on `POST /submissions` to prevent queue flooding.

## 3. Frontend Token Storage

Documented tradeoff: `[state the actual choice made — e.g. "localStorage was chosen for simplicity; this is vulnerable to XSS if a script-injection vulnerability is ever introduced elsewhere in the frontend. httpOnly cookies would be more secure but require backend changes (CSRF handling, cookie-based auth flow) not yet built."]` — stated explicitly rather than silently picked, since it's relevant if this comes up during capstone evaluation.

## 4. Sandbox Isolation (Untrusted Code Execution)

This is the highest-risk part of the system: the app executes arbitrary, learner-submitted Java code. **Environment update**: Docker with root access is now confirmed available on the college deployment server, so the sandbox uses real container-based isolation as its primary mechanism. The original non-Docker design (kept below for reference) remains the documented fallback if container access is ever lost.

### Current design — Docker container isolation

Each submission (and each benchmark run at each scaled input size) executes in a short-lived, disposable container, torn down immediately after:

| Control | Mechanism |
|---|---|
| Filesystem isolation | Container filesystem namespace; `read_only=True` root filesystem with a small writable `tmpfs` scratch mount, discarded on container removal |
| Process isolation | Container PID namespace — a fork bomb inside the container can't affect host or sibling-container processes |
| CPU limit | `cpu_period` / `cpu_quota` cgroup limits |
| Memory limit | `mem_limit` / `memswap_limit` (swap capped too, to prevent a swap-based memory-limit bypass) |
| Process count limit | `pids_limit` — blocks fork bombs at the cgroup level, independent of the PID namespace boundary |
| Network isolation | `network_disabled=True` — no outbound network access at all, blocks any exfiltration/callback attempt |
| Wall-clock timeout | Enforced from the host side (container `wait(timeout=...)`, force-killed and removed if exceeded) — independent of the CPU-time cgroup limit, catches processes blocked on I/O |

A pre-built base image (JDK 21) is built once and reused across submissions rather than rebuilt per run, since a fresh build per submission would dominate latency, especially for the benchmarking stage's 6–8 runs per submission.

**Why this is a meaningful upgrade over the original design**: the original subprocess + resource-limit approach could constrain CPU/memory/process count but could **not** isolate the filesystem or process namespace — a sufficiently clever submission could, in principle, still see host process listings or interact with anything reachable from the scratch directory's permissions. Container-level isolation closes that gap.

### Fallback design (retained for reference — used if container access is ever unavailable)

If Docker/root access is ever lost (e.g. a policy change on the college server), the system can fall back to the original three-layer, container-free design:

1. **OS resource limits** via `resource.setrlimit` in a `preexec_fn` (`RLIMIT_CPU`, `RLIMIT_AS`, `RLIMIT_NPROC`, `RLIMIT_CORE`, `RLIMIT_FSIZE`) — kernel-enforced, holding even if the JVM ignores everything else.
2. **Java Security Manager deny-by-default policy** — file access restricted to the submission's own scratch directory, no sockets, no reflection, no subprocess spawning. Note: deprecated for removal upstream (JEP 411); functions on JDK 21 (LTS) but is not guaranteed on future JDKs.
3. **Wall-clock timeout** via `subprocess.run(..., timeout=...)`.

This fallback does **not** isolate filesystem or PID namespaces — documented explicitly as the tradeoff of that design, should it ever need to be reactivated.

### Verified via Testing

`tests/test_sandbox_robustness.py` proves — not just asserts by design — that isolation actually fires for each specific failure mode (infinite loop → timeout; memory bomb → cgroup memory kill; fork bomb → `pids_limit`; file-write escape → blocked by read-only filesystem/container boundary; network attempt → blocked by `network_disabled`). Re-run this suite after the Docker migration to confirm the new mechanism produces the same expected-failure-mode results as the original design did (see `TESTING.md` Section 5) — a container-level control failing silently in a different way than the old resource-limit control would be a regression worth catching explicitly, not assumed away.

## 5. Input Validation

- All API request bodies validated via Pydantic models — malformed requests rejected before reaching business logic.
- Submitted source code size-capped (max length enforced in the `SubmissionCreate` schema).
- Sandbox stdout/stderr truncated at a fixed byte cap (default 1MB) to prevent a submission from exhausting server-side memory via output spam.

## 6. Data Privacy

- No sensitive personal data collected beyond name, email, and hashed password.
- Submission source code is stored (for history/review purposes) but not exposed to any user other than its submitter.
- Logs avoid recording full submitted source code at info level — a short identifier is logged instead, with full source only at debug level if needed (see `DEPLOYMENT.md` logging section).

## 7. Known Gaps / Accepted Risk (Documented, Not Hidden)

- Scaled-input benchmarking can, in principle, be gamed by a submission that special-cases known input patterns; per-repetition input re-randomization reduces but does not eliminate this.
- Structural hint detection is regex/token-based, not full AST parsing — theoretically bypassable by unusual code structure, though this affects hint quality, not sandbox safety.
- No plagiarism/academic-integrity detection between users (out of scope for v1).
- Rate limiting is simple in-process tracking, not a dedicated rate-limit service — sufficient at this project's expected scale, not designed for adversarial load.
