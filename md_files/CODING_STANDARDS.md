# AlgoLens — Coding Standards

## General Principles

- Prefer clarity over cleverness — this is a capstone project other people (evaluators, future contributors) will need to read and understand quickly.
- A module's docstring/header comment should explain *why* a non-obvious design choice was made (e.g. why the sandbox uses `preexec_fn` instead of a container), not just what the code does.
- Root-cause fixes over patches. If a bug is found, trace it to its actual source before fixing (see the correctness-checking bug fix in project history for the model to follow — investigate first, fix at the source, add a regression test).

## Python (Backend)

- **Formatting**: follow PEP 8. Use 4-space indentation, no tabs.
- **Naming**:
  - `snake_case` for functions, variables, modules.
  - `PascalCase` for classes (`CompiledSubmission`, `SandboxResult`).
  - `UPPER_SNAKE_CASE` for module-level constants (`DEFAULT_CPU_SECONDS`).
  - Private/internal helpers prefixed with a single underscore (`_apply_os_limits`, `_run_limited`).
- **Type hints**: required on all function signatures. Use `from __future__ import annotations` where helpful for forward references.
- **Dataclasses over dicts** for structured internal values (`SandboxResult`, `SandboxLimits`, `ClassificationResult`) — gives type safety and self-documentation over passing raw dicts around.
- **Pydantic models** for all API request/response shapes — never return raw ORM objects or raw dicts from a route.
- **Docstrings**: module-level docstrings for anything non-obvious (the sandbox executor, the complexity classifier) should explain the *design rationale*, not just restate the code.
- **Error handling**: never use a bare `except Exception: pass`. Catch specific exceptions; if a broad catch is genuinely needed, log it. This class of bug (a swallowed exception silently defaulting to "success") is exactly what caused the correctness-checking regression — see `CHANGELOG.md`.
- **Logging**: use the standard `logging` module, never bare `print()`. See `DEPLOYMENT.md` for the logging configuration used in production.

## SQLAlchemy / Models

- One model per file under `app/models/`, grouped by domain (`user.py`, `problem.py`, `submission.py`).
- UUID string primary keys (`str(uuid.uuid4())`), not auto-incrementing integers — avoids leaking submission/user counts and simplifies eventual multi-instance deployment.
- Foreign keys always explicit (`ForeignKey("problems.id")`), relationships defined both directions where used.

## React / Frontend

- Functional components with hooks — no class components.
- **Naming**: `PascalCase` for component files and component names, `camelCase` for functions/variables, `kebab-case` for non-component asset files.
- Tailwind **core utility classes only** — this environment has no Tailwind compiler, so custom config extensions (custom colors in `tailwind.config`, etc.) won't apply. Palette values from `UI_UX.md` should be applied via inline style or a small CSS variables file, not assumed to work as custom Tailwind classes.
- Component hierarchy should mirror the screens in `UI_UX.md` — one top-level component per screen, broken into smaller pieces only where genuinely reused (e.g. `VerdictBanner`, `TestCaseResultsPanel`, `ComplexityChart`).
- No `localStorage`/`sessionStorage` access inside components without going through a single auth/session module — token storage logic lives in one place, not scattered across components.

## Comparators / Verdict Logic

- Comparator types (`exact`, `numeric_tolerance`, `sorted`, `custom`) are looked up via a dict dispatch (`_COMPARATORS`), not an `if/elif` chain — makes adding a new comparator type additive rather than requiring an edit to existing logic.
- Any new verdict state added to `Submission.status` must be reflected in: the backend enum/comment listing valid values, `API.md`'s status table, and the frontend's verdict-banner styling — all three, not just the backend.

## Commit Messages

- Format: `<area>: <short imperative description>` — e.g. `sandbox: add Java Security Manager policy`, `frontend: fix redirect-after-login losing intended destination`.
- Reference the root cause in bug-fix commits, not just the symptom (e.g. `pipeline: fix vacuous all() over empty test case list, not just empty-submission case`).

## Testing Conventions

See `TESTING.md` for the full strategy. Naming convention: `test_<unit_under_test>_<scenario>.py` / `test_<scenario>` for individual test functions. Integration tests that actually compile/run Java are marked `@pytest.mark.integration` and kept separate from fast unit tests.
