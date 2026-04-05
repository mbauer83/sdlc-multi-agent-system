"""ERP model writer operations package.

This package is the tool/infrastructure side of deterministic writing.
The MCP server should depend on these modules, not embed the logic.
"""

from .types import WriteResult
from .help import write_help
from .entity import create_entity
from .connection import create_connection
from .diagram import create_diagram

__all__ = [
    "WriteResult",
    "write_help",
    "create_entity",
    "create_connection",
    "create_diagram",
]
