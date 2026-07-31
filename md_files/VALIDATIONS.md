# AlgoLens — Validation Requirements

Instructions for implementing input validation across AlgoLens. Every field a user can submit — via the API directly or through the frontend — must be validated on the **backend** (source of truth) and mirrored on the **frontend** (fast feedback, better UX). Never trust frontend validation alone; the API must reject invalid input even if the frontend is bypassed entirely (curl, a modified request, a future non-browser client).

## General Principles

1. **Validate at the boundary.** Pydantic schemas (`app/schemas/`) are the single point where request data is validated before it reaches business logic. Business logic (`app/services/`) should be able to assume its inputs are already well-formed — don't scatter ad-hoc validation checks deep inside service functions.
2. **Fail with a specific, actionable error.** "Invalid input" is not acceptable. "Email must be a valid email address" / "Password must be at least 8 characters" is. FastAPI's Pydantic validation errors already do this by default — don't override them with generic messages.
3. **Reject, don't silently coerce.** If a field is out of range or malformed, reject the request (`422 Unprocessable Entity`) rather than silently clamping/truncating/defaulting it. Silent coercion is exactly the failure mode that caused the correctness-checking bug in project history (something being silently accepted when it should have been rejected) — don't repeat that pattern in input validation either.
4. **Validate on both ends, but the backend is authoritative.** Frontend validation exists to give immediate feedback and avoid wasted round-trips — it is never a substitute for backend validation.
5. **Whitelist, don't blacklist**, wherever practical (e.g. comparator types are an enum of known values, not "reject known-bad strings").
6. **Every new field added anywhere in the schema gets a validation rule added here and enforced in code — no exceptions**, including fields added in later phases (see `PHASES.md`).

## Error Response Format

Standardize validation error responses so the frontend can render them consistently:

```json
{
  "detail": [
    {
      "field": "email",
      "message": "value is not a valid email address"
    }
  ]
}
```

FastAPI's default Pydantic validation error shape is close to this already — confirm it's actually surfaced to the frontend as structured data, not flattened into an opaque string the UI can only show verbatim.

---

## Auth Fields

| Field | Rules |
|---|---|
| `name` | Required, 1–120 characters, trimmed of leading/trailing whitespace, reject if empty after trimming |
| `email` | Required, valid email format (`EmailStr`), lowercased before storage/comparison to prevent duplicate accounts differing only by case, max 255 characters |
| `password` (registration) | Required, minimum 8 characters, maximum 128 characters (prevents hashing-cost DoS via absurdly long input). Do not enforce complex composition rules (must-have-symbol, etc.) — length is a better predictor of strength and composition rules push users toward predictable substitutions. Never log the raw password anywhere, including in validation-error paths. |
| `password` (login) | Required, non-empty — do not apply the registration length rules here (an existing user's password might predate a rule change; reject on wrong password via hash comparison, not via a length check that could lock out real accounts) |

**Backend**: enforce via `RegisterRequest`/`LoginRequest` Pydantic schemas (see `app/schemas/auth.py`).
**Frontend**: mirror min-length/format checks inline in the registration/login form before submit, but always handle and display the backend's validation error too (don't assume frontend checks caught everything).

### Duplicate email handling
Already covered by `409 Conflict` on registration (see `API.md`) — confirm the check is case-insensitive, matching the lowercasing rule above.

---

## Problem & Test Case Fields (admin/seed-time, not user-facing in v1)

Even though problems are seeded via `app/seed.py` rather than a public endpoint in v1, validate them anyway — a malformed seed entry should fail loudly at seed time, not silently produce a broken problem a learner encounters later.

| Field | Rules |
|---|---|
| `title` | Required, 1–200 characters |
| `description` | Required, non-empty |
| `difficulty` | Must be one of `easy` \| `medium` \| `hard` — enum, not free text |
| `optimal_time_complexity` / `optimal_space_complexity` | Must match one of the known complexity class labels used by the classifier (`O(1)`, `O(log n)`, `O(n)`, `O(n log n)`, `O(n^2)`, `O(n^3)`, `O(2^n)`) — a typo'd label here would silently break the gap-detection comparison in `app/services/complexity.py`'s `is_gap()`; validate against the same `COMPLEXITY_ORDER` list that function uses, don't duplicate the list |
| `generator_key` | Must correspond to an actually-registered key in `app/problems_data/registry.py` — fail seed-time if not, rather than failing later at first benchmark attempt |
| `TestCase.comparator_type` | Must be one of `exact` \| `numeric_tolerance` \| `sorted` \| `custom` — enum |
| `TestCase.input` / `expected_output` | Required, non-empty |
| `InefficiencySignature.pattern_type` | Must correspond to an actually-registered detector key in `app/services/hints.py`'s `_PATTERN_CHECKS` — same fail-loud-at-seed-time principle |

If/when a community problem-submission feature is built (see `ARCHITECTURE.md` Future Work), these same rules become user-facing input validation, not just seed-time sanity checks — revisit this section when that phase starts.

---

## Submission Fields

| Field | Rules |
|---|---|
| `problem_id` | Required, must be a valid UUID matching an existing `Problem` row — `404`, not a generic `422`, if the problem doesn't exist (distinguish "malformed ID" from "well-formed ID that doesn't exist") |
| `source_code` | Required, non-empty after trimming whitespace, minimum a few characters (reject trivially-empty submissions at the API layer, in addition to the pipeline's own compile-failure handling — this is a UX improvement, not a substitute for the compile-time check, since the compile-time check is what actually guarantees correctness) |
| `source_code` max length | Cap at a defined maximum (e.g. 20,000 characters) to prevent absurdly large submissions from bloating storage or slowing down compilation. Reject with a clear "source code exceeds maximum length" message, not a silent truncation (silent truncation would compile a *different* program than the one the user actually wrote, which is far worse than an outright rejection). |
| `source_code` content | Do **not** attempt to blacklist "dangerous" Java keywords/imports at the validation layer (e.g. rejecting `Runtime`, `ProcessBuilder`, `Socket` by string matching) — this is a weak, bypassable control and creates a false sense of security. The actual security boundary is the Docker sandbox (see `SECURITY.md`), not string filtering on the source. Validation here is about well-formedness and size, not attempting to pre-judge code safety. |

**Backend**: `SubmissionCreate` Pydantic schema (`app/schemas/submission.py`) — add the min-length/max-length constraints if not already present.
**Frontend**: disable the Submit button while the editor is empty; show the character-count limit if approaching the max; never attempt client-side "dangerous code" detection for the same reason it's not done server-side at the validation layer.

---

## Query Parameters

| Endpoint | Parameter | Rules |
|---|---|---|
| `GET /users/{id}/history` | `limit` | Integer, default 20, min 1, max 100 (prevent a client requesting an unbounded page size) |
| `GET /users/{id}/history` | `offset` | Integer, default 0, min 0 |
| Any `{id}` path parameter | — | Must be a syntactically valid UUID before even querying the database — reject malformed IDs with `422` rather than letting a malformed string reach a database query |

---

## Path/Resource Ownership Validation

Distinct from field-level validation, but a form of input validation worth stating explicitly: any endpoint receiving a resource ID (`submission_id`, history `{id}`) must validate that **the authenticated user actually owns that resource** before returning data — already specified in `API.md` and `SECURITY.md`, restated here because it's a validation concern too, not just an authorization one. A well-formed but *unauthorized* ID should return `403`/`404` (per the existing convention of not leaking existence), never a `500` from an unhandled case.

---

## File/Environment Configuration Validation (startup-time, not request-time)

- `app/config.py` (`Settings`) should fail fast at application startup if required environment variables are missing or malformed (e.g. `JWT_SECRET` unset or still the placeholder `"change-me-in-prod"` value in a non-dev environment) — don't let the app start silently misconfigured and fail mysteriously later on the first real request.
- `DATABASE_URL` should be validated as a parseable connection string at startup, not discovered to be malformed only when the first query runs.
- `BENCHMARK_INPUT_SIZES` (comma-separated integers) should be parsed and validated (all positive integers, ascending order) at startup — a malformed value here would silently break every benchmarking run.

---

## Frontend Form Validation Conventions

- Every form field with a backend validation rule above gets a matching inline frontend check, using the same limits (don't let the frontend allow something the backend will reject — that's a broken UX loop, not real validation).
- Show validation errors **next to the field**, not only as a toast/banner — consistent with the plain, direct copy convention in `UI_UX.md`.
- Never block form submission on a frontend check that isn't also enforced by the backend — if the two ever diverge, the backend wins and the frontend rule should be corrected to match, not the other way around.
- The code editor (Monaco) should show a live character count once nearing the `source_code` max length, not just reject on submit.

---

## Testing Requirement

Every rule in this document needs a corresponding test, following the conventions in `TESTING.md`:

- Add `tests/test_validation.py` (unit-level, fast) covering: each auth field's boundary cases (empty, too long, malformed email, password exactly at the 8-character boundary on both sides), submission `source_code` boundary cases (empty, exactly at max length, one character over), malformed UUID path parameters, and out-of-range pagination parameters.
- Table-driven, matching the style already used in `tests/test_correctness_comparators.py`.
- Each test asserts the **specific** error response (status code + field-level message), not just "request failed" — the same principle already applied to sandbox robustness testing (assert the specific failure mode, not a generic non-success).

## Exit Criteria

- [ ] Every field in every Pydantic schema under `app/schemas/` has an explicit rule matching this document, not relying on default/unconstrained types.
- [ ] `app/config.py` fails fast on missing/placeholder required settings at startup.
- [ ] Seed-time validation catches a deliberately malformed problem/test case/signature entry before it reaches the database.
- [ ] `tests/test_validation.py` passes, covering every table above.
- [ ] Frontend forms mirror every backend rule and display field-level errors returned from the backend, not just their own local checks.
- [ ] No blacklist-style "dangerous code" string filtering was added anywhere — confirmed the sandbox remains the sole security boundary for submitted code content.
