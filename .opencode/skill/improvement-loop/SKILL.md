---
name: improvement-loop
description: Use when the user asks to analyze, improve, audit, review, optimize, or "next"-step this app (API 5L Pipe) using an iterative one-change-at-a-time loop. Enforces the strict Analyze -> Justify -> Propose -> ASK PERMISSION -> Implement -> Verify protocol and the priority order (critical bugs, performance, UX/UI, missing features, code quality). Trigger keywords: improve, iyileştir, analiz, audit, review, optimization, next, sonraki, bug, performans.
---

# Improvement Loop

This project is a real production app: **API 5L PSL1/PSL2 & BOTAŞ Pipe QA/QC,
Wall Thickness & ITP Smart Auditor Suite**.

- Backend: FastAPI, `app.py` (routes/API), `core/` (engines: `pipe_qaqc_engine.py`,
  `verification_engine.py`, `wall_thickness_engine.py`, `derating_engine.py`,
  `bevel_engine.py`, `straightness_engine.py`, `erw/sawl/sawh_engine.py`,
  `hydrostatic_engine.py`, `pdf_exporter.py`, `excel_exporter.py`,
  `itp_audit_engine.py`, `database.py`).
- Frontend: `templates/index.html` (single big template), `templates/report_template.html`,
  `static/js/*.js` (`app.js`, visualizers), `static/css`.
- Tests: `tests/test_pipe_suite.py` (pytest), `tests/test_regression_golden.py`
  (golden masters in `tests/golden_master/`).
- Domain: pipeline engineering standards — API 5L, ASME B31.8/B36.10, EN 10204.
  Numeric correctness is safety-critical. Never invent standard values.

## The strict loop

Run exactly one improvement per cycle, in this priority order:

1. Critical bugs (wrong results, crashes, data loss, security)
2. Performance issues (slow endpoints, heavy exports, UI jank)
3. UX/UI improvements
4. Missing or weak features
5. Code quality / maintainability

### Step 1 — Analyze
Dispatch the analysis subagents (in parallel) to scan the codebase and return
candidate findings. Then pick the **single** most impactful item. Do NOT list
multiple options to the user.

- `qa-auditor` — bugs, crashes, wrong math, unhandled input
- `perf-analyst` — performance bottlenecks
- `ux-reviewer` — UI/UX friction
- `feature-scout` — missing/weak features
- `refactor-architect` — maintainability

### Step 2 — Justify
State: what the issue is, why it matters (user/system impact), and the risk if
left unfixed. Keep it to a few sentences.

### Step 3 — Propose
Give a precise solution: root cause + fix for bugs; before/after for UI;
expected behavior + flow for features; refactor approach for code quality.
Include the concrete files/functions to change (`file_path:line`).

### Step 4 — Ask permission (MANDATORY, cannot be skipped)
End the turn with exactly:

> Do you want me to implement this improvement?

Do NOT edit any file, run any mutating command, or continue until the user
explicitly approves. If the user says no/skip, discard and wait.

### Step 5 — Implement (only after approval)
Make the minimal change. Follow existing conventions (no new libraries unless
already in `requirements.txt`). No comments unless asked. Show the file-level
modifications.

### Step 6 — Verify
Dispatch `verifier`, and explain how to test, the expected result, and edge
cases covered. Prefer `pytest` (existing suites) and `ruff check .`.

## Continuation rule
After implementing and verifying, stop and wait. When the user says **"next"**
(or "sonraki"), restart from Step 1 for the next best improvement. Never batch
multiple improvements into one cycle.

## Constraints
- One item per cycle. No laundry lists.
- High-impact, production-ready only. No theoretical advice.
- Preserve `$schema` and unrelated config.
- Numeric/standard behavior changes require a test or golden-master check.
