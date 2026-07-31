# AlgoLens — UI/UX

## 1. Product Framing

AlgoLens is a **competitive coding platform**, in the same category as LeetCode — not a "lab" or "graded exam" tool. The interface should feel like a familiar coding judge first. The one thing that makes AlgoLens different — measured complexity compared against the optimum — is a distinct, clearly-separated section shown *after* the standard verdict, the way LeetCode shows a runtime/memory percentile after judging, not the framing for the whole product.

## 2. Design Principles

- **Avoid generic AI-UI defaults.** Specifically ruled out: warm cream background + terracotta accent, near-black + neon accent, and broadsheet/hairline-rule newspaper layouts. These are common defaults, not choices made for this product.
- **One real signature moment.** The runtime-curve comparison (learner's curve vs. optimal curve, log-log axes) is the product's most characteristic visual and should read as considered, not templated.
- **Restraint everywhere else.** Problem list and history screens are quiet, secondary surfaces — the visual budget is spent on the results screen.
- **Plain, direct copy.** LeetCode's own verdict language ("Accepted," "Wrong Answer") is used directly. No backend vocabulary ("pipeline," "job," "empirical classifier") in user-facing text.

## 3. Palette — Orange Accent Theme

Replaces an earlier dark-blue theme. Specific named values (fill in actual hex chosen during implementation — recorded here once finalized):

| Role | Value | Usage |
|---|---|---|
| Background | `[hex]` | App background |
| Surface | `[hex]` | Cards, panels |
| Text primary | `[hex]` | Body/heading text |
| Text secondary | `[hex]` | Muted/supporting text |
| Border | `[hex]` | Dividers, card borders |
| **Orange accent** | `[hex]` | Primary actions, active nav, brand elements — reserved, not reused as a verdict color |

**Semantic verdict colors** (kept visually distinct from both each other and from the orange accent):

| Verdict | Color role |
|---|---|
| Accepted | Green |
| Wrong Answer | Red |
| Compilation Error / Runtime Error | Amber/orange-adjacent, visually distinguishable from Wrong Answer's red |
| Time Limit Exceeded | Distinguished via icon/label, not just color, to avoid a fourth competing hue |

**Difficulty tags** (Easy/Medium/Hard) use a separate green/amber/red convention from verdict colors — kept visually distinguishable from verdict colors where both could appear in the same view (e.g. problem list showing both difficulty and a solved/attempted indicator).

## 4. Typography

- Display/heading face: used with restraint, not for every heading.
- Body face: complementary, for descriptions and UI copy.
- Monospace face: for the code editor and any displayed input/output/data — this choice matters since the product has real code and real numbers on screen constantly.

## 5. Screens

### Landing page (public, unauthenticated)
1. Hero — concrete headline about the actual mechanism (measures runtime growth, compares to optimal), not vague SaaS language. Primary CTA: Sign up. Secondary: Log in.
2. How it works — 3-step sequence (solve → get judged → see complexity comparison), reusing the curve-comparison visual concept.
3. Differentiation section — a few sentences on what makes this different from a standard judge.
4. Problem bank preview — 3–4 real problem cards (fetched from `GET /problems`, not fabricated), difficulty-tagged.
5. Final CTA.

No fabricated stats or testimonials.

### Problem list (authenticated)
- Table/list layout: solved/attempted status indicator, title, difficulty tag, (optional, only if backend-tracked) acceptance stat.
- Quiet, secondary screen — not over-designed.

### Problem detail + editor
- Problem description alongside a Monaco-based Java editor.
- Submit action. (Run vs. Submit distinction deferred — see `TASKS.md` backlog — until sample-vs-hidden test case data exists on the backend; not faked in the UI.)

### Results screen — the hero screen
1. **Verdict banner** — immediate, prominent, styled per the semantic verdict colors (Accepted / Wrong Answer / Compilation Error / Runtime Error / Time Limit Exceeded).
2. **Test case results panel** — per-case input, expected output, actual output, pass/fail, shown directly beneath the banner.
3. **Complexity comparison section** (separate, after the above) — empirical complexity classification with confidence, the reference optimal-complexity curve, and the learner's measured curve on shared log-log axes.
4. **Structural hint** — shown only when a gap exists, in a direct and specific voice, never revealing the optimal solution's code.

### Submission history
- List of past judge runs: timestamp, problem, verdict, complexity classification. Quiet styling consistent with the problem list.

## 6. Technical Constraints

- React, Tailwind (core utility classes only — no Tailwind compiler in this environment, custom config extensions won't apply).
- Monaco Editor for code input.
- Recharts or D3 for the complexity curve chart.
- Fully responsive down to mobile.
- Visible keyboard focus states throughout.
- Respects `prefers-reduced-motion` — the curve-reveal signature moment must still land correctly without relying on motion.
- Any animation is deliberate and singular (e.g. one orchestrated curve reveal), not scattered hover/scroll effects.

## 7. Auth-Gated Navigation

- Problems, problem detail, results, and history routes require a valid session — logged-out access attempts redirect to login.
- Redirect-back-after-login preserves the originally-requested destination (not a generic dashboard dump).
- Nav reflects auth state: logged-out shows Login/Sign up; logged-in shows user name + logout.
- Token storage: `[document the actual choice made — e.g. localStorage, with the known XSS tradeoff noted, vs. httpOnly cookies requiring backend support]`.
