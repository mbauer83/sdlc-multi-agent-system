---
schema-id: learning-entry
version: 1.0.0
status: Approved — Stage 4.6
governed-by: framework/learning-protocol.md
---

# Schema: Learning Entry

Specifies the required fields and validation rules for a learning entry stored in an agent role's `learnings/` directory. Governed by `framework/learning-protocol.md §2`.

---

## Frontmatter Fields

| Field | Type | Required | Validation |
|---|---|---|---|
| `learning-id` | string | Yes | Pattern `[A-Z]+-L-\d{3}` or `[A-Z]+-SYNTH-\d{3}`; unique within the role's `learnings/index.yaml`; never reused |
| `agent` | string | Yes | One of: `SA`, `SwA`, `DE`, `DO`, `QA`, `PM`, `PO`, `SM`, `CSCO` |
| `phase` | list[string] | Yes | Non-empty; each element one of: `Prelim`, `A`, `B`, `C`, `D`, `E`, `F`, `G`, `H`, `req-mgmt`; or `all` for cross-phase applicability |
| `artifact-type` | string | Yes | One of the schema-id values from `framework/artifact-schemas/`: `architecture-vision`, `business-architecture`, `application-architecture`, `data-architecture`, `technology-architecture`, `implementation-plan`, `test-strategy`, `safety-constraint-overlay`, `architecture-contract`, `change-record`, `requirements-register`, `diagram-catalog`; or `process` for procedural/protocol mistakes |
| `trigger-event` | string | Yes | One of: `feedback-revision`, `algedonic`, `gate-veto`, `incorrectly-raised-cq`, `synthesis` |
| `error-type` | string | Yes | One of: `omission` (something required was not checked or included), `wrong-inference` (an assumption made from available data was incorrect), `wrong-scope` (the artifact's scope was too narrow or too broad), `protocol-skip` (a required procedure step was not followed), `calibration` (a threshold, classification, or priority was systematically miscalibrated) |
| `importance` | string | Yes | One of: `S1` (critical — algedonic signal, user escalation, safety-relevant), `S2` (significant — revision required, gate veto, avoidable CQ), `S3` (minor — no revision, low recurrence expectation) |
| `applicability` | string | Yes | `domain-agnostic` (applies regardless of industry/system type) or `domain:<specific-domain>` (e.g., `domain:healthcare`, `domain:finance`, `domain:industrial-control`). When uncertain: use `domain-agnostic`; synthesis step may refine. |
| `generated-at.phase` | string | Yes | The ADM phase active when the learning was generated |
| `generated-at.sprint` | integer | Yes | Sprint number when the learning was generated |
| `generated-at.engagement` | string | Yes | The engagement-id |
| `promoted` | boolean | Yes | `false` initially; `true` when promoted to `enterprise-repository/knowledge-base/learnings/`; `enterprise-superseded` when a newer promoted version supersedes this entry |
| `synthesis-superseded` | string | No | If this entry has been superseded by a synthesis entry: the synthesis `learning-id`; `query_learnings` skips entries with this field set |
| `synthesised-from` | list[string] | No | For synthesis entries only: list of source entry `learning-id`s |

---

## Body Sections

### `## Trigger` (Required)

1–3 sentences describing the concrete situation that generated this learning. Must include: which phase, which artifact (by type and section if applicable), and what was initially wrong or missing. This section is for authoring context — it is **not** injected at retrieval time.

**Validation:** Must not be empty. Must reference a specific artifact type or phase. Must not contain the word "always" alone as the correction (too vague).

### `## Correction` (Required — primary runtime artifact)

1–3 sentences stating the actionable correction in **imperative first-person voice**. This is the text injected into the agent's working context at retrieval time (Step 0.L). Requirements:
- **Imperative**: begins with "When" or an imperative verb
- **Self-contained**: comprehensible without reading the Trigger section
- **Specific**: names the artifact section, field, or check that should differ
- **Concise**: 1–3 sentences maximum; no hedging language

**Anti-patterns (reject at record_learning validation):**
- Vague generalizations: "be more careful about X"
- Negative-only framing without positive alternative: "don't forget to check Y"
- Engagement-specific references that won't generalize: "in the healthcare system, remember that..."
- Tautologies: "always follow the protocol correctly"

**Validation:** Must not be empty. Must be ≤ 300 characters per sentence. Must not contain phrases: "be more careful", "don't forget", "remember to always".

### `## Context` (Optional)

Additional detail useful for deciding whether to promote to enterprise level. Not injected at retrieval time. May include: reference to the specific engagement scenario, additional domain context, or notes on recurrence across sprints.

---

## Index Entry Fields (`learnings/index.yaml`)

| Field | Type | Required | Description |
|---|---|---|---|
| `learning-id` | string | Yes | Same as frontmatter |
| `phase` | list[string] | Yes | Same as frontmatter; used for filtering |
| `artifact-type` | string | Yes | Same as frontmatter; used for filtering |
| `error-type` | string | Yes | Same as frontmatter |
| `importance` | string | Yes | Same as frontmatter; used for sorting |
| `applicability` | string | Yes | Same as frontmatter; used for domain filtering |
| `correction-summary` | string | Yes | First sentence of the `## Correction` section; used for quick review without reading full file |
| `file` | string | Yes | Filename of the full entry (e.g., `CSCO-L-001.md`) |
| `promoted` | boolean/string | Yes | Same as frontmatter |
| `synthesis-superseded` | string | No | Set when superseded by synthesis; causes `query_learnings` to skip this entry |

---

## Validation Rules for `record_learning()` Tool

The `record_learning()` tool (Stage 5b, `universal_tools.py`) validates:

1. All required frontmatter fields present and of correct type
2. `learning-id` matches pattern and is unique in index
3. `agent` matches the calling agent's role (path constraint — an agent cannot write learnings to another role's repository)
4. `trigger-event` matches one of the controlled vocabulary values
5. `error-type` matches controlled vocabulary
6. `importance` is one of S1, S2, S3
7. `applicability` matches `domain-agnostic` or `domain:<non-empty-string>`
8. `## Correction` section: present, non-empty, ≤ 900 characters total, does not contain anti-pattern phrases
9. `## Trigger` section: present, non-empty

On validation failure: raise `LearningSchemaError` with field name and reason; do not write the entry.

---

## Example Entry

```markdown
---
learning-id: CSCO-L-003
agent: CSCO
phase: [A]
artifact-type: architecture-vision
trigger-event: feedback-revision
error-type: omission
importance: S2
applicability: domain-agnostic
generated-at:
  phase: A
  sprint: 1
  engagement: eng-001
promoted: false
---

## Trigger

During Phase A gate review, SA's AV described the system as an "internal analytics platform" and classified it as non-safety. CSCO accepted this classification. On Iteration 1 feedback from the user, it emerged the system processes employee performance review data — personal data subject to GDPR. The safety classification should have been Safety-Related (regulatory breach risk). Iteration 1 revision was required.

## Correction

When an AV describes a system as "internal" or "analytics", explicitly check: does this system collect, store, or process data about the organization's own employees (performance, health, location, communications)? If yes, treat as a PII-processing system with GDPR/equivalent applicability regardless of whether it is customer-facing.

## Context

"Internal" is routinely used to imply low-sensitivity when the opposite may be true. Employee data is frequently more sensitive than customer data in some jurisdictions. This pattern is likely to recur across any HR, workforce analytics, or internal operations system engagement.
```
