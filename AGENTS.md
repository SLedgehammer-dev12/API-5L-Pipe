# AGENTS.md — API 5L Pipe

Production QA/QC suite: **FastAPI backend + vanilla JS / Three.js frontend** for
API 5L PSL1/PSL2 & BOTAŞ pipe quality assurance, wall-thickness design and ITP
auditing. Numeric correctness is safety-critical.

## Layout
- `app.py` — FastAPI app and HTTP routes.
- `core/` — domain engines (`pipe_qaqc_engine.py`, `verification_engine.py`,
  `wall_thickness_engine.py`, `derating_engine.py`, `bevel_engine.py`,
  `straightness_engine.py`, `erw/sawl/sawh_engine.py`, `hydrostatic_engine.py`,
  `pdf_exporter.py`, `excel_exporter.py`, `itp_audit_engine.py`,
  `database.py`, `schemas.py`, `i18n.py`).
- `templates/` — `index.html` (main UI), `report_template.html`.
- `static/js/` — `app.js` and visualizers; `static/css/` styles.
- `tests/` — `test_pipe_suite.py` (pytest) and `test_regression_golden.py`
  (golden masters under `tests/golden_master/`).

## Commands
- Run app: `python3 run.py` (or `./run.sh`)
- Tests: `pytest -q`
- Golden masters: `pytest tests/test_regression_golden.py -q`
- Lint: `ruff check .`

Always run `ruff check .` and the relevant `pytest` selection before declaring a
change done. Any change to numeric/standard behavior must be covered by a test
or a golden-master check.

## Conventions
- Match existing style; do not add comments unless asked.
- Do not add dependencies not already in `requirements.txt` without approval.
- Keep the Turkish/English i18n consistent (`core/i18n.py`,
  `static/js/i18n.js`).

## Improvement workflow (Dual Antigravity & OpenCode Support)
This repo uses the `improvement-loop` skill and the `improver` orchestrator agent along with 7 specialized subagents (`qa-auditor`, `perf-analyst`, `ux-reviewer`, `feature-scout`, `refactor-architect`, `verifier`, `ponytail-reviewer`):
- Run strictly one high-impact change at a time, always asking permission before implementing.
- Use `/improve` to start a cycle and `/next` to continue.
- **Antigravity**: Discovers custom agents under `.agents/agents/` and skills under `.agents/skills/`. Subagents are dispatched via `invoke_subagent`.
- **OpenCode**: Discovers custom agents under `.opencode/agent/` (and `.opencode/agents/`) and skills under `.opencode/skill/` (and `.agents/skills/`). Subagents are dispatched via the task tool.

## Ponytail (Lazy Senior Dev Mode)
This repository integrates **Ponytail** (`@dietrichgebert/ponytail`) for minimal, high-impact diffs and lean code quality:
- The best code is the code never written. Solve problems with the least new code (YAGNI, stdlib first, minimal diffs).
- Never add unnecessary abstractions, wrappers, or unapproved dependencies.
- Never cut safety boundaries: validation at trust boundaries, error handling that prevents data loss, security, accessibility, and safety-critical engineering calculations.
- Intentional shortcuts must be tagged: `# shortcut: <ceiling>, <upgrade trigger>`.
- Supported in both **OpenCode** and **Antigravity**:
  - `/ponytail [lite|full|ultra|off]` — Switch lazy senior dev intensity.
  - `/ponytail-review` — Quality review of changes (correctness, safety, scale, tests, lean).
  - `/ponytail-audit` — Full repository quality and dead-code audit.
  - `/ponytail-debt` — Collect and report `shortcut:` debt ledger.
  - `/ponytail-gain` — Benchmark efficiency scoreboard.
  - `/ponytail-help` — Quick reference.
<!-- stageshow-skill-integration -->
## Stageshow UI Illustration & Demo Skill (Antigravity & OpenCode)

- **`stageshow`** (`.agents/skills/stageshow/SKILL.md` | OpenCode slash command: `/stageshow`): Builds faux product UI stills, feature cards, bento grids, and cursor walkthrough demos in React + CSS with automated filming/verification (`scripts/film.mjs --gate`).
- **Host Adaptation Guide:** See [`.agents/skills/stageshow/references/project-adaptation.md`](.agents/skills/stageshow/references/project-adaptation.md) for this project's web UI stack (`FastAPI + Jinja2/HTML + CSS/JS web arayüzü (`app.py`, `templates/`, `static/`)`) and integration steps.
