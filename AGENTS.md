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

## Improvement workflow
This repo uses the `improvement-loop` skill and the `improver` agent: one
high-impact change at a time, always asking permission before implementing.
Use `/improve` to start a cycle and `/next` to continue.
