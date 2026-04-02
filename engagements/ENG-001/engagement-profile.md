---
engagement-id: ENG-001
engagement-name: "Initial Engagement"
entry-point: EP-0           # EP-0 | EP-A | EP-B | EP-C | EP-D | EP-G | EP-H
status: active              # active | closed | archived
cycle-level: capability     # strategic | segment | capability
parent-cycle-id: null       # ID of parent ADM cycle if this is a child cycle
created: 2026-04-02

# Target project repository — the software project being built, analysed, or changed.
# This is a SEPARATE git repository. The framework never commits into it.
# See framework/architecture-repository-design.md §2.4 and §3.4
target-repository:
  url: null                             # Set before starting work
                                        # e.g. git@github.com:org/project.git
                                        #   or /home/user/my-project
  default-branch: main
  local-clone-path: target-repo/        # relative to this engagement directory; .gitignored
---

# Engagement Profile: ENG-001

## Scope

*[To be completed during entry assessment — describe what this engagement is building, changing, or analysing. Include: the problem being solved, the target system, the business context, and any known constraints.]*

## Target Project

**Repository URL:** *[to be configured in engagement-profile.md frontmatter and engagements-config.yaml]*  
**Technology stack:** *[to be determined during entry assessment / Phase A]*  
**Current state:** *[new project / existing codebase / in-production system]*

## Entry Point Assessment

**Entry Point:** EP-0 (Cold Start)  
**Warm-Start Artifacts:** None — engagement starts from scratch.  
**Pre-emptive CQs:** See `clarification-log/` for any open CQs raised during entry assessment.

## ADM Phase Scope

| Phase | Status | Notes |
|---|---|---|
| Preliminary | pending | |
| A — Architecture Vision | pending | |
| B — Business Architecture | pending | |
| C — Information Systems Architecture | pending | |
| D — Technology Architecture | pending | |
| E — Opportunities & Solutions | pending | |
| F — Migration Planning | pending | |
| G — Implementation Governance | pending | |
| H — Architecture Change Management | pending | |
| Requirements Management | ongoing | Runs throughout |

## Constraints and Context

*[To be populated during Phase A.]*

## External Sources Active for This Engagement

*[List source-ids from `external-sources/` that are relevant to this engagement.]*
