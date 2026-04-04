"""
archimate_types.py — Canonical type registries for the SDLC agent model.

This module is the **single source of truth** for:
  - Valid `artifact-type` values in entity and connection frontmatter
  - Valid `artifact-type` values for connection files (per diagram language)
  - Valid `element-type` values in §display ###archimate blocks
  - Valid `relationship-type` values in §display ###archimate blocks

Usage
-----
- ``ModelVerifier`` imports from this module for all type validation.
- Documentation (``framework/artifact-schemas/entity-conventions.md`` and
  ``framework/diagram-conventions.md``) references this file as authoritative.
- When a new ArchiMate element type or connection type is added to the model,
  update this file **first**, then update documentation to match.

Design notes
------------
- **Entity types use the ArchiMate ontology exclusively.** There are no separate
  entity types for activity, sequence, or class diagram languages — all model
  entities are ArchiMate elements regardless of which diagram language renders them.
- **Connection types are organised per diagram language.** Activity diagrams,
  sequence diagrams, use-case diagrams, and ER diagrams each have their own
  relationship vocabulary; ArchiMate structural relationships form a separate set.
  Connections files live under ``connections/<language>/<type>/`` reflecting this.
- Each registry is provided in two forms:
  1. An organised ``dict[str, frozenset[str]]`` grouped by layer/language.
  2. A flat ``frozenset[str]`` (``ALL_*``) for O(1) membership tests.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Entity artifact-type values
# (the ``artifact-type:`` field in entity frontmatter)
# ---------------------------------------------------------------------------

ENTITY_TYPES_BY_LAYER: dict[str, frozenset[str]] = {
    "motivation": frozenset(
        {
            "stakeholder",
            "driver",
            "assessment",
            "goal",
            "outcome",
            "principle",
            "requirement",
            "architecture-constraint",
            "meaning",
            "value",
        }
    ),
    "strategy": frozenset(
        {
            "capability",
            "value-stream",
            "resource",
            "course-of-action",
        }
    ),
    "business": frozenset(
        {
            "business-actor",
            "business-role",
            "business-collaboration",
            "business-interface",
            "business-process",
            "business-function",
            "business-interaction",
            "business-event",
            "business-service",
            "business-object",
            "contract",
            "representation",
            "product",
        }
    ),
    "application": frozenset(
        {
            "application-component",
            "application-collaboration",
            "application-interface",
            "application-function",
            "application-interaction",
            "application-process",
            "application-event",
            "application-service",
            "data-object",
        }
    ),
    "technology": frozenset(
        {
            "technology-node",
            "device",
            "system-software",
            "technology-collaboration",
            "technology-interface",
            "path",
            "communication-network",
            "technology-function",
            "technology-process",
            "technology-interaction",
            "technology-event",
            "technology-service",
            "artifact",
        }
    ),
    "physical": frozenset(
        {
            "equipment",
            "facility",
            "distribution-network",
            "material",
        }
    ),
    "implementation": frozenset(
        {
            "work-package",
            "deliverable",
            "implementation-event",
            "plateau",
            "gap",
        }
    ),
}

#: Flat union of all valid entity ``artifact-type`` values.
ALL_ENTITY_TYPES: frozenset[str] = frozenset().union(*ENTITY_TYPES_BY_LAYER.values())


# ---------------------------------------------------------------------------
# Connection artifact-type values
# (the ``artifact-type:`` field in connection frontmatter, prefixed by language)
# ---------------------------------------------------------------------------

CONNECTION_TYPES_BY_LANGUAGE: dict[str, frozenset[str]] = {
    "archimate": frozenset(
        {
            "archimate-composition",
            "archimate-aggregation",
            "archimate-assignment",
            "archimate-realization",
            "archimate-serving",
            "archimate-access",
            "archimate-influence",
            "archimate-association",
            "archimate-specialization",
            "archimate-flow",
            "archimate-triggering",
        }
    ),
    "er": frozenset(
        {
            "er-one-to-many",
            "er-many-to-many",
            "er-one-to-one",
        }
    ),
    "sequence": frozenset(
        {
            "sequence-synchronous",
            "sequence-asynchronous",
        }
    ),
    "activity": frozenset(
        {
            "activity-sequence-flow",
            "activity-decision",
        }
    ),
    "usecase": frozenset(
        {
            "usecase-include",
            "usecase-extend",
            "usecase-association",
        }
    ),
}

#: Flat union of all valid connection ``artifact-type`` values.
ALL_CONNECTION_TYPES: frozenset[str] = frozenset().union(
    *CONNECTION_TYPES_BY_LANGUAGE.values()
)


# ---------------------------------------------------------------------------
# ArchiMate element-type values
# (the ``element-type:`` field in §display ###archimate blocks)
# Follows ArchiMate 3 UpperCamelCase naming convention.
# ---------------------------------------------------------------------------

ARCHIMATE_ELEMENT_TYPES_BY_LAYER: dict[str, frozenset[str]] = {
    "motivation": frozenset(
        {
            "Stakeholder",
            "Driver",
            "Assessment",
            "Goal",
            "Outcome",
            "Principle",
            "Requirement",
            "Constraint",
            "Meaning",
            "Value",
        }
    ),
    "strategy": frozenset(
        {
            "Capability",
            "ValueStream",
            "Resource",
            "CourseOfAction",
        }
    ),
    "business": frozenset(
        {
            "BusinessActor",
            "BusinessRole",
            "BusinessCollaboration",
            "BusinessInterface",
            "BusinessProcess",
            "BusinessFunction",
            "BusinessInteraction",
            "BusinessEvent",
            "BusinessService",
            "BusinessObject",
            "Contract",
            "Representation",
            "Product",
        }
    ),
    "application": frozenset(
        {
            "ApplicationComponent",
            "ApplicationCollaboration",
            "ApplicationInterface",
            "ApplicationFunction",
            "ApplicationInteraction",
            "ApplicationProcess",
            "ApplicationEvent",
            "ApplicationService",
            "DataObject",
        }
    ),
    "technology": frozenset(
        {
            "Node",
            "Device",
            "SystemSoftware",
            "TechnologyCollaboration",
            "TechnologyInterface",
            "Path",
            "CommunicationNetwork",
            "TechnologyFunction",
            "TechnologyProcess",
            "TechnologyInteraction",
            "TechnologyEvent",
            "TechnologyService",
            "Artifact",
        }
    ),
    "physical": frozenset(
        {
            "Equipment",
            "Facility",
            "DistributionNetwork",
            "Material",
        }
    ),
    "implementation": frozenset(
        {
            "WorkPackage",
            "Deliverable",
            "ImplementationEvent",
            "Plateau",
            "Gap",
        }
    ),
}

#: Flat union of all valid ArchiMate ``element-type`` values.
ALL_ARCHIMATE_ELEMENT_TYPES: frozenset[str] = frozenset().union(
    *ARCHIMATE_ELEMENT_TYPES_BY_LAYER.values()
)


# ---------------------------------------------------------------------------
# ArchiMate relationship-type values
# (the ``relationship-type:`` field in §display ###archimate connection blocks)
# Follows ArchiMate 3 UpperCamelCase naming convention.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# ArchiMate grouping stereotype names
# (the ``<<Stereotype>>`` applied to grouping rectangle containers)
# One stereotype per ArchiMate layer; no generic <<Grouping>> permitted in diagrams.
# Grouping containers must not have inline color overrides — the stereotype
# provides the only permissible background.
# ---------------------------------------------------------------------------

ARCHIMATE_GROUPING_STEREOTYPES: frozenset[str] = frozenset(
    {
        "MotivationGrouping",
        "StrategyGrouping",
        "BusinessGrouping",
        "ApplicationGrouping",
        "TechnologyGrouping",
        "PhysicalGrouping",
        "ImplementationGrouping",
    }
)

# ---------------------------------------------------------------------------
# ArchiMate relationship-type values
# (the ``relationship-type:`` field in §display ###archimate connection blocks)
# Follows ArchiMate 3 UpperCamelCase naming convention.
# ---------------------------------------------------------------------------

ARCHIMATE_RELATIONSHIP_TYPES: frozenset[str] = frozenset(
    {
        "Composition",
        "Aggregation",
        "Assignment",
        "Realization",
        "Serving",
        "Access",
        "Influence",
        "Association",
        "Specialization",
        "Flow",
        "Triggering",
    }
)
