---
description: Start one cycle of the strict improvement loop (analyze -> propose ONE -> ask permission).
agent: improver
---

Load the `improvement-loop` skill and begin a new cycle for this app.

Optional focus from the user: $ARGUMENTS

Do this:
1. Dispatch `qa-auditor`, `perf-analyst`, `ux-reviewer`, `feature-scout`, and
   `refactor-architect` in parallel for their single highest-impact findings.
2. Rank by priority (critical bugs > performance > UX/UI > features > quality)
   and select EXACTLY ONE improvement.
3. Justify it, then propose a precise solution with `file_path:line` targets.
4. End with "Do you want me to implement this improvement?" and STOP.

Do not list multiple items, and do not edit anything before explicit approval.
