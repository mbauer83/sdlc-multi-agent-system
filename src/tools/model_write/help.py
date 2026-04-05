from __future__ import annotations

from src.common.archimate_types import ALL_CONNECTION_TYPES, ALL_ENTITY_TYPES
from src.common.model_write import (
    ARCHIMATE_STEREOTYPE_TO_CONNECTION_TYPE,
    CONNECTION_TYPES,
    ENTITY_TYPES,
)


def write_help() -> dict[str, object]:
    entity_types_sorted = sorted(list(ALL_ENTITY_TYPES))
    connection_types_sorted = sorted(list(ALL_CONNECTION_TYPES))
    missing_entity_mappings = sorted([t for t in entity_types_sorted if t not in ENTITY_TYPES])
    missing_connection_mappings = sorted([t for t in connection_types_sorted if t not in CONNECTION_TYPES])
    return {
        "entity_types": entity_types_sorted,
        "connection_types": connection_types_sorted,
        "entity_type_mapping_complete": len(missing_entity_mappings) == 0,
        "connection_type_mapping_complete": len(missing_connection_mappings) == 0,
        "missing_entity_type_mappings": missing_entity_mappings,
        "missing_connection_type_mappings": missing_connection_mappings,
        "archimate_relationship_stereotypes": sorted(list(ARCHIMATE_STEREOTYPE_TO_CONNECTION_TYPE.keys())),
        "notes": [
            "Entity IDs in PUML should use underscore aliases (e.g. APP_001) to be inferable.",
            "ArchiMate connection inference requires stereotypes like : <<serving>> on the connection line.",
            "Matrix diagrams can be created with model_create_matrix (.md), with optional auto-linking of entity IDs.",
            "Writer tools refuse to write outside engagements/<id>/work-repositories/.",
        ],
    }
