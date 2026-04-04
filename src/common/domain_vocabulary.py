"""
SDLC Multi-Agent System — domain vocabulary for search and NLP.

Provides the canonical bidirectional synonym map used by:
  - ``ModelRepository.search`` / ``search_artifacts`` (keyword expansion)
  - ``LearningStore.query_learnings`` (optional synonym expansion in Stage 5b)
  - Any future NLP pipeline operating on framework artifact text

Keeping this here (not inside model_query.py or archimate_types.py) allows
all search/query components to share a single maintained vocabulary without
circular imports.

Coverage
--------
Three semantic domains are covered:

1. **Agent abbreviations ↔ expanded role titles**
   PM ↔ "project manager", SA ↔ "solution architect", etc.

2. **Protocol / concept abbreviations ↔ expanded terms**
   CQ ↔ "clarification request/question", ALG ↔ "algedonic", ADM ↔ "TOGAF phases", etc.

3. **ArchiMate artifact-id prefix ↔ element type**
   BPR ↔ "business process", APP ↔ "application component", etc.
   Also common domain concepts → related terms for improved recall.

Usage
-----
Import ``expand_tokens`` for the one-hop expansion used in scoring::

    from src.common.domain_vocabulary import expand_tokens, DOMAIN_SYNONYMS

    expanded = expand_tokens(["pm", "decision"])
    # → ["pm", "decision", "project", "manager", "orchestration", ...]
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Primary synonym map  (key → list of expansion terms, all lowercase)
# ---------------------------------------------------------------------------
# Keys are the "short" or "abbreviation" form.  Values are the expanded terms.
# The reverse index is built automatically below so lookups are bidirectional.

DOMAIN_SYNONYMS: dict[str, list[str]] = {
    # -----------------------------------------------------------------------
    # Agent abbreviations ↔ role descriptions
    # -----------------------------------------------------------------------
    "pm":   ["project", "manager", "orchestration", "coordinator", "supervisor"],
    "sa":   ["solution", "architect", "architecture", "business", "motivation"],
    "swa":  ["software", "architect", "application", "technology", "principal", "engineer"],
    "do":   ["devops", "platform", "infrastructure", "deployment", "pipeline"],
    "de":   ["developer", "implementing", "implementation", "coding", "coder"],
    "qa":   ["quality", "assurance", "testing", "validation", "test"],
    "po":   ["product", "owner", "requirements", "backlog", "user", "stories"],
    "csco": ["safety", "compliance", "security", "risk", "chief", "officer"],
    "sm":   ["sales", "marketing", "market", "swot", "commercial"],

    # -----------------------------------------------------------------------
    # Protocol / concept abbreviations
    # -----------------------------------------------------------------------
    "cq":     ["clarification", "question", "request", "query", "answer"],
    "alg":    ["algedonic", "escalation", "signal", "bypass", "fast", "path"],
    "adm":    ["architecture", "development", "method", "phase", "togaf"],
    "adr":    ["decision", "record", "architectural"],
    "erp":    ["entity", "registry", "pattern"],
    "bdd":    ["behavior", "driven", "scenario", "gherkin", "feature"],
    "puml":   ["plantuml", "diagram", "uml", "visualization"],
    "ep":     ["entry", "point", "engagement", "onboarding"],
    "vsm":    ["viable", "system", "model", "cybernetic"],
    "sib":    ["standard", "information", "base", "approved"],
    "fts":    ["full", "text", "search", "index"],
    "raci":   ["responsible", "accountable", "consulted", "informed"],
    "iia":    ["inferred", "annotated", "source", "evidence"],
    "pr":     ["pull", "request", "code", "review", "merge"],
    "ci":     ["continuous", "integration", "pipeline", "build"],

    # -----------------------------------------------------------------------
    # ArchiMate artifact-id prefixes ↔ element types
    # -----------------------------------------------------------------------
    "bpr":  ["business", "process"],
    "bsv":  ["business", "service"],
    "bfn":  ["business", "function"],
    "bev":  ["business", "event"],
    "bob":  ["business", "object"],
    "bif":  ["business", "interface"],
    "bco":  ["business", "collaboration"],
    "act":  ["actor", "role", "agent", "business"],
    "rol":  ["role", "business", "function"],
    "cap":  ["capability", "strategic"],
    "vs":   ["value", "stream"],
    "res":  ["resource", "strategic"],
    "app":  ["application", "component"],
    "asv":  ["application", "service"],
    "afn":  ["application", "function"],
    "aif":  ["interface", "port", "application"],
    "aev":  ["application", "event"],
    "dob":  ["data", "object"],
    "aco":  ["application", "collaboration"],
    "stk":  ["stakeholder"],
    "drv":  ["driver", "motivation"],
    "req":  ["requirement"],
    "cst":  ["constraint"],
    "pri":  ["principle"],
    "gol":  ["goal", "objective"],
    "out":  ["outcome"],
    "mea":  ["meaning", "representation"],
    "val":  ["value"],
    "ass":  ["assessment"],
    "wp":   ["work", "package", "implementation"],
    "del":  ["deliverable", "output"],
    "gap":  ["gap", "analysis"],
    "plt":  ["plateau", "migration"],
    "nod":  ["node", "technology"],
    "ssw":  ["system", "software", "platform"],
    "tsv":  ["technology", "service"],
    "art":  ["artifact", "deployment"],

    # -----------------------------------------------------------------------
    # Common domain concepts ↔ related terms (improves recall for natural-language queries)
    # -----------------------------------------------------------------------
    "event":      ["workflow", "eventstore", "record", "log", "publish"],
    "handoff":    ["transfer", "delivery", "artifact", "cross-role"],
    "sprint":     ["iteration", "cycle", "planning", "agile"],
    "skill":      ["phase", "capability", "invocation", "prompt"],
    "learning":   ["correction", "feedback", "mistake", "improvement", "reflexion"],
    "promotion":  ["enterprise", "elevation", "governance", "board"],
    "snapshot":   ["state", "checkpoint", "persistence", "replay"],
    "brownfield": ["existing", "legacy", "migration", "reverse", "onboarding"],
    "greenfield": ["new", "fresh", "forward", "start", "cold"],
    "gateway":    ["port", "interface", "adapter", "boundary"],
    "policy":     ["rule", "constraint", "principle", "governance"],
    "trace":      ["traceability", "link", "reference", "dependency"],
    "scaffold":   ["template", "stub", "skeleton", "boilerplate"],
    "gate":       ["checkpoint", "review", "approval", "criteria", "evaluation"],
    "diagram":    ["puml", "visualization", "view", "model"],
    "entity":     ["artifact", "model", "element", "instance"],
    "connection": ["relation", "link", "edge", "association", "realization"],
}

# ---------------------------------------------------------------------------
# Auto-built reverse index  (expansion term → list of abbreviation keys)
# ---------------------------------------------------------------------------
REVERSE_SYNONYMS: dict[str, list[str]] = {}
for _key, _vals in DOMAIN_SYNONYMS.items():
    for _val in _vals:
        REVERSE_SYNONYMS.setdefault(_val, []).append(_key)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def expand_tokens(tokens: list[str]) -> list[str]:
    """Return *tokens* plus one-hop synonym expansion (order preserved, no duplicates).

    Both directions are followed: ``"pm"`` expands to ``["project", "manager", …]``
    and ``"manager"`` expands to include ``"pm"`` (via the reverse index).

    This gives significantly better recall for natural-language discovery queries
    against a corpus that uses both formal abbreviations (``PM Agent``) and
    descriptive prose (``"the project manager coordinates specialist agents"``).

    Parameters
    ----------
    tokens:
        Lowercased tokens from a query (output of :func:`tokenize_query`).

    Returns
    -------
    list[str]
        Original tokens followed by expansion terms, deduplicated.

    Examples
    --------
    >>> expand_tokens(["pm", "decision"])
    ['pm', 'decision', 'project', 'manager', 'orchestration', 'coordinator', 'supervisor']
    """
    seen: set[str] = set(tokens)
    expanded: list[str] = list(tokens)
    for tok in tokens:
        for syn in DOMAIN_SYNONYMS.get(tok, []):
            if syn not in seen:
                expanded.append(syn)
                seen.add(syn)
        for syn in REVERSE_SYNONYMS.get(tok, []):
            if syn not in seen:
                expanded.append(syn)
                seen.add(syn)
    return expanded


def agent_abbreviations() -> dict[str, str]:
    """Return the canonical mapping of agent abbreviation → display name.

    Useful for UI labelling and system-prompt display.
    """
    return {
        "PM":   "Project Manager",
        "SA":   "Solution Architect",
        "SwA":  "Software Architect / Principal Engineer",
        "DO":   "DevOps / Platform Engineer",
        "DE":   "Implementing Developer",
        "QA":   "QA Engineer",
        "PO":   "Product Owner",
        "CSCO": "Chief Safety & Compliance Officer",
        "SM":   "Sales & Marketing Manager",
    }


def archimate_prefix_to_type() -> dict[str, str]:
    """Return the canonical mapping of artifact-id prefix → ArchiMate element type.

    Used for display, reporting, and filter-hint generation.
    """
    return {
        "STK": "stakeholder",
        "DRV": "driver",
        "ASS": "assessment",
        "GOL": "goal",
        "OUT": "outcome",
        "PRI": "principle",
        "REQ": "requirement",
        "CST": "constraint",
        "MEA": "meaning",
        "VAL": "value",
        "CAP": "capability",
        "VS":  "value-stream",
        "RES": "resource",
        "COA": "course-of-action",
        "ACT": "business-actor",
        "ROL": "business-role",
        "BCO": "business-collaboration",
        "BPR": "business-process",
        "BFN": "business-function",
        "BEV": "business-event",
        "BSV": "business-service",
        "BOB": "business-object",
        "BIF": "business-interface",
        "PRD": "product",
        "CTR": "contract",
        "RPR": "representation",
        "APP": "application-component",
        "ACO": "application-collaboration",
        "AIA": "application-interaction",
        "APR": "application-process",
        "AFN": "application-function",
        "AEV": "application-event",
        "ASV": "application-service",
        "AIF": "application-interface",
        "DOB": "data-object",
        "NOD": "node",
        "DEV": "device",
        "SSW": "system-software",
        "TSV": "technology-service",
        "ART": "artifact",
        "NET": "network",
        "TFN": "technology-function",
        "TEV": "technology-event",
        "TIF": "technology-interface",
        "TPR": "technology-process",
        "WP":  "work-package",
        "DEL": "deliverable",
        "GAP": "gap",
        "PLT": "plateau",
        "IEV": "implementation-event",
    }
