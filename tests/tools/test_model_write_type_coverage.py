"""Coverage tests: every supported type must be handled by writer mappings.

These are not BDD scenarios; they are exhaustive safety checks ensuring that
new registry entries in src/common/archimate_types.py cannot silently become
unwriteable.
"""

from __future__ import annotations

from src.common.archimate_types import ALL_CONNECTION_TYPES, ALL_ENTITY_TYPES
from src.common.model_write import CONNECTION_TYPES, ENTITY_TYPES


def test_writer_entity_type_mapping_covers_all() -> None:
    missing = sorted([t for t in ALL_ENTITY_TYPES if t not in ENTITY_TYPES])
    assert missing == [], f"Missing entity mappings for: {missing}"


def test_writer_connection_type_mapping_covers_all() -> None:
    missing = sorted([t for t in ALL_CONNECTION_TYPES if t not in CONNECTION_TYPES])
    assert missing == [], f"Missing connection mappings for: {missing}"
