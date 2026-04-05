"""model_write_ops.py — Compatibility facade.

The implementation was split into smaller modules under src/tools/model_write/.
This module remains as a stable import path for MCP server code and tests.
"""

from __future__ import annotations

from typing import Literal

from src.common.model_write import DiagramConnectionInferenceMode

from src.tools.model_write import (
    WriteResult,
    create_connection,
    create_diagram,
    create_entity,
    create_matrix,
    write_help,
)


WriteRepoScope = Literal["engagement"]

__all__ = [
    "DiagramConnectionInferenceMode",
    "WriteRepoScope",
    "WriteResult",
    "write_help",
    "create_entity",
    "create_connection",
    "create_diagram",
    "create_matrix",
]
