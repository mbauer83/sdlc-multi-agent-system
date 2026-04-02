---
name: Authoring approach for agent/skill files
description: How the user wants agent and skill files authored — quality bar, review process, validation concerns
type: feedback
---

User wants comprehensive review after authoring batches — not just "files created" confirmation. Specifically:
- Validate phase coverage, interfaces, handoff contracts, CQ protocol usage
- Check non-linear ADM handling (trigger=revisit, phase_visit_count)
- Ensure all 7 EP entry behaviours are present in every AGENT.md
- Ensure discovery-from-project-state is properly handled (scan before asking)
- Ensure incomplete-data starting scenarios are covered

**Why:** User explicitly requested review pass on Stage 3 output, caught gaps in discovery behavior and ALG misuse.

**How to apply:** After every authoring batch, do a validation pass reading the key files before marking complete. Fix issues found (ALG IDs, missing constraints, discovery gaps) before closing the stage.
