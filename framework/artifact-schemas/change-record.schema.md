# Schema: Change Record (`CR`)

**Version:** 1.0.0  
**ADM Phase:** H  
**Owner:** Solution Architect (primary); Software Architect/PE for technology-domain changes  
**Consumed by:** All agents whose artifacts are affected, CSCO (gate), Project Manager (log)  

---

## 1. Purpose

The Change Record is the formal artifact for any change request entering Phase H. It documents the change, its classification, its impact on existing baselined artifacts, the decision taken, and the update actions required. It is the authorisation for architecture artifacts to be revised and re-baselined.

---

## 2. Required Sections

### 2.1 Summary Header
- `artifact-type: change-record`
- `safety-relevant:` true if the change touches a safety-relevant component or constraint
- `csco-sign-off:` required if safety-relevant; required for Major and Safety-Critical changes

### 2.2 Change Request

| Field | Value |
|---|---|
| Change ID | CR-nnn |
| Title | |
| Raised By | Agent role |
| Raised In | Sprint ID |
| Source | Defect / Requirement Change / Technology Obsolescence / Regulatory / Business Change / Architecture Inconsistency |
| Description | [Full description of what has changed or what needs to change] |
| Urgency | Immediate / Next Sprint / Planned |

### 2.3 Change Impact Classification

| Classification | Selected | Rationale |
|---|---|---|
| Minor | Yes / No | |
| Significant | Yes / No | |
| Major | Yes / No | |
| Safety-Critical | Yes / No | |

**Classification** per `agile-adm-cadence.md §10`. Only one class applies; escalate to the highest applicable.

### 2.4 Affected Artifacts

| Artifact ID | Current Version | Change Required | New Version |
|---|---|---|---|
| AV / BA / AA / DA / TA / IP / TS / AC / SCO | | | |

### 2.5 Safety Impact Analysis

**Required if `safety-relevant: true`. CSCO must author or co-author this section.**

- Does this change introduce any new UCAs? [Yes / No — if yes, list them]
- Does this change retire or modify any existing safety constraints? [Yes / No — list affected SC-nnn]
- Does this change require the STAMP control structure to be updated? [Yes / No]
- CSCO assessment: [Accept / Conditional Accept / Reject with rationale]

### 2.6 Decision Record

| Field | Value |
|---|---|
| Decision | Approved / Rejected / Deferred |
| Decision By | PM (Minor) / SA+PM (Significant) / All affected owners + CSCO (Major/Safety-Critical) |
| Conditions | [Any conditions on approval] |
| Sprint for Implementation | |

### 2.7 Implementation Actions

| Action ID | Description | Owner | Target Artifact | Target Sprint | Status |
|---|---|---|---|---|---|
| ACT-nnn | | | | | Open / Complete |

---

## 3. Version History

| Version | Sprint | Agent | Change Summary |
|---|---|---|---|
| 0.1.0 | | | Change request raised |
| 1.0.0 | | | Decision recorded; approved |
