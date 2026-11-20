# Stageshow Host Adaptation: API 5L Pipe QA/QC & Wall Thickness Suite

This document adapts the portable `stageshow` skill (from `benjitaylor/skills`) for **API 5L Pipe QA/QC & Wall Thickness Suite** so both **Antigravity** and **OpenCode** discover, run, and verify it identically using repo-relative paths.

## Host Web Stack & Entrypoints

- **Stack:** FastAPI + Jinja2/HTML + CSS/JS web arayüzü (`app.py`, `templates/`, `static/`)
- **Key Web UI Paths:**
- `app.py`
- `templates/index.html`
- `templates/report_template.html`
- `static/css/`
- `static/js/`

## Dual-Harness Discovery & Invocation

- **Antigravity:** Automatically discovers `.agents/skills/stageshow/SKILL.md` via `.agents/skills/stageshow/` (progressive disclosure) and reads `AGENTS.md`. Ask naturally (e.g., *"Use stageshow to build a product demo card for..."*).
- **OpenCode:** Discovers `stageshow` via OpenCode's native `skill` tool AND via the `/stageshow` slash command defined in `.opencode/command/stageshow.md`. Invoke `/stageshow <brief>` or mention `stageshow` in your prompt.

## Integration Mode (FastAPI / HTML / DOM Frontend)

This project serves a non-React HTML/CSS/JS web UI without a React bundler at runtime. Author and verify Stageshow scenes inside `.agents/skills/stageshow`, then embed the verified output:

1. **Author & Rehearse in Standalone Playground:**
   - Copy the closest gold example under `.agents/skills/stageshow/examples/` to `.agents/skills/stageshow/examples/<your-scene>/` and iterate via the bundled Vite dev server.
2. **Embed into Host Web UI (`static/` and `templates/index.html`):**
   - **Interactive bundle / iframe:** Run `npm --prefix .agents/skills/stageshow run build` (or bundle the scene entry) and serve the self-contained static HTML/JS output via an `<iframe>` or route under `static/` and `templates/index.html`.
   - **Zero-JS crisp stills / video:** Film `@2x` stills (`--still`) or MP4/GIF loops with `node .agents/skills/stageshow/scripts/film.mjs` and render them directly in `static/` and `templates/index.html`.

## Setup & Verification Commands (Run from Repository Root)

```bash
# 1. Install Stageshow playground & verification dependencies (first time only)
npm --prefix .agents/skills/stageshow install

# 2. Launch standalone previewer (optional during authoring)
npm --prefix .agents/skills/stageshow run dev

# 3. Typecheck and CSS collision checks
npm --prefix .agents/skills/stageshow run typecheck
npm --prefix .agents/skills/stageshow run check:css

# 4. Film & gate verification (replace URL and selector for your scene)
node .agents/skills/stageshow/scripts/film.mjs '<preview_or_app_url>' --select '#example' --gate
node .agents/skills/stageshow/scripts/film.mjs '<preview_or_app_url>' --select '#example' --width 390 --gate
node .agents/skills/stageshow/scripts/film.mjs '<preview_or_app_url>' --select '#example' --states --gate
```
