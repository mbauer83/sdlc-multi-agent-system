"""
SourceAdapter: read-only protocol for all external source adapters.

Every adapter (Confluence, Jira, git source, user uploads, target repos)
implements this protocol so the agent tool layer has a uniform query surface.
All queries emit a source.queried EventStore event — the tool wiring in
universal_tools.py handles event emission; adapters must not emit events.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class SourceAdapter(Protocol):
    """
    Read-only source adapter.

    Implementations are registered in the engagement's source registry and
    called via the universal read_source tool.  No adapter may write to any
    external system.
    """

    def query(self, query: str) -> str:
        """
        Execute a free-text query against this source.

        Returns a plain-text summary of the most relevant results.
        The caller is responsible for emitting source.queried EventStore events.
        """
        ...

    @property
    def source_id(self) -> str:
        """Unique identifier for this source (matches config file stem)."""
        ...
