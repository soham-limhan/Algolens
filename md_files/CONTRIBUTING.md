# Contributing to AlgoLens

This is a capstone project, currently developed solo with AI-assisted (Antigravity) build workflows. This document describes the workflow so it's reproducible if the project grows a team, gets picked up by collaborators, or is handed off.

## Workflow

1. **Check `TASKS.md`** for the current phase and what's in progress vs. planned.
2. **Branch naming**: `feature/<short-name>`, `fix/<short-name>`, `docs/<short-name>` off `main`.
3. **Before writing code**: if the change touches the sandbox, correctness checking, or the complexity classifier, read the relevant section of `ARCHITECTURE.md` first — these modules have specific design constraints (no Docker, no root, resource-limit-based isolation) that aren't obvious from the code alone.
4. **Investigate before fixing.** For bug reports, trace the actual root cause before patching — don't add a special case that only handles the reported symptom. See the correctness-checking bug fix (`CHANGELOG.md`) as the model: the reported symptom was "empty code passes," but the actual bug was in test-case-loading/comparator logic, and fixing only the empty-submission case would have left the deeper bug (wrong-but-non-empty answers also passing) in place.
5. **Add regression tests** for every bug fix — see `TESTING.md`.
6. **Update documentation alongside code**, not after: a new endpoint updates `API.md` in the same change; a new verdict state updates `API.md`, `CODING_STANDARDS.md`'s note on verdict handling, and the frontend's verdict styling together.
7. **Open a PR** (or, for solo work, a clearly-scoped commit) referencing which `TASKS.md` item it completes.

## Using AI Coding Assistants (Antigravity or similar)

This project has been built substantially via structured prompts to an AI coding agent. When writing a build prompt:

- State hard constraints explicitly up front (e.g. "no Docker, SSH-only server, no sudo") — an agent will default to the most common solution (Docker) unless told not to.
- Include explicit **non-goals** — what NOT to build in this pass — to prevent scope creep into adjacent work (e.g. "no Jenkinsfile yet" during backend-only phases).
- For bug fixes, instruct the agent to **investigate and report root cause before fixing**, not guess-fix — see `AI_CONTEXT.md` for the standing instruction on this.
- Request a written summary of what was actually done vs. what was deferred/flagged, so `TASKS.md` can be updated accurately.

See `AI_CONTEXT.md` for the full set of standing instructions given to AI assistants working on this repo.

## Code Review Checklist

- [ ] Does this change match the constraints in `ARCHITECTURE.md` (no Docker, no root, async submission flow)?
- [ ] Are new DB fields reflected in `DATABASE.md`?
- [ ] Are new/changed endpoints reflected in `API.md`?
- [ ] Are new verdict states or UI states reflected in `UI_UX.md`?
- [ ] Does a bug fix include a regression test, and does the test fail on the pre-fix code?
- [ ] Is untrusted input (submitted code, problem generator output) still only executed through the sandbox — never directly imported/eval'd?
- [ ] Has `TASKS.md` been updated?

## Reporting Issues

When reporting a bug, include:
- What was submitted/done, and what was expected vs. actual behavior.
- Whether it reproduces consistently or intermittently (relevant for sandbox timing-sensitive issues).
- The submission ID or relevant log excerpt if available (see `DEPLOYMENT.md` for log locations).
