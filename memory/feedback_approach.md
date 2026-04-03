---
name: Authoring approach and review expectations
description: How the user wants agent/skill files authored, quality bar, and tool usage rules for this project
type: feedback
---

**Post-authoring review is required after every batch.** Not just "files created" confirmation:
- Validate phase coverage, interfaces, handoff contracts, CQ protocol usage
- Check non-linear ADM handling (trigger=revisit, phase_visit_count)
- Ensure all 7 EP entry behaviours are present in every AGENT.md
- Ensure discovery-from-project-state is properly handled (scan before asking)
- Ensure incomplete-data starting scenarios are covered

**Why:** User explicitly requested review pass on Stage 3 output; caught gaps in discovery behavior and ALG misuse. Review pass on Stage 4 caught YAML frontmatter bug and wrong complexity-class values.

**How to apply:** After every authoring batch, do a validation pass reading the key files before marking complete. Fix issues found before closing the stage.

---

**Do NOT use background agents to edit files.** Background agents are denied the Edit tool and cannot make file changes. For bulk edits across many files, write a Python/Bash script and run it directly via the Bash tool.

**Why:** Launching 8 parallel agents to edit 43 skill files wasted ~50% of a session's token budget when all agents were blocked by Edit permission denial.

**How to apply:** When a task requires editing N files (N > 3), default to a Bash/Python script. Use agents only for read-only research tasks (Grep, Read, WebFetch).

---

**Keep repo memory/ up-to-date and committed** — `memory/` at the repo root is git-tracked and must reflect current project state. After completing any significant work, update `memory/project_state.md` and `memory/MEMORY.md` and commit them.

**Why:** User explicitly requires this; the memory files in the repo are the authoritative record across sessions.
