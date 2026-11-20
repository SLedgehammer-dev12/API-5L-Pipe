---
description: Build polished faux product UI illustrations, hero cards, cursor walkthroughs, and animated UI demos with Stageshow
---

Build or refine the requested product UI illustration, feature card, bento grid, or animated cursor walkthrough ($ARGUMENTS).

Follow the Stageshow skill in `.agents/skills/stageshow/SKILL.md` and this repository's host integration guide in `.agents/skills/stageshow/references/project-adaptation.md`:
1. Read `.agents/skills/stageshow/SKILL.md` and `.agents/skills/stageshow/references/project-adaptation.md` first.
2. Choose the closest gold example under `.agents/skills/stageshow/examples/`, read `.agents/skills/stageshow/references/craft.md` and `.agents/skills/stageshow/references/framing.md`, and adapt tokens/chrome/copy to this project's web UI.
3. Integrate into this project using the stack pattern in `references/project-adaptation.md` (direct React `kit/` import for React frontends, or standalone Stageshow playground build / `st.components.v1.html` / static embed / filmed still for FastAPI, HTML/JS, and Streamlit hosts).
4. Verify with `npm --prefix .agents/skills/stageshow run typecheck`, `npm --prefix .agents/skills/stageshow run check:css`, and `node .agents/skills/stageshow/scripts/film.mjs ... --gate` until rehearsal passes.
