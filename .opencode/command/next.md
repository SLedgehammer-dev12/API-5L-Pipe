---
description: Continue the improvement loop with the next best improvement.
agent: improver
---

Continue the improvement loop. Restart from Step 1 for the NEXT best
improvement (do not repeat a previously completed or rejected item; check
`CHANGELOG.md` / git log for what was already done).

Dispatch the analysis subagents in parallel, rank the findings, select ONE,
justify it, propose a precise solution with `file_path:line` targets, then end
with "Do you want me to implement this improvement?" and STOP.
