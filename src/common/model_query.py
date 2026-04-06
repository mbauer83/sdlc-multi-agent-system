"""ERP v2.0 Model Query public API facade."""

from __future__ import annotations

from src.common.model_query_repository import ModelRepository
from src.common.model_query_types import (
    ArtifactSummary,
    ConnectionRecord,
    DiagramRecord,
    DuplicateArtifactIdError,
    EntityRecord,
    RepoMount,
    SearchHit,
    SearchResult,
    SemanticSearchProvider,
)


def main(argv: list[str] | None = None) -> int:
    from src.common.model_query_cli import main as cli_main

    return cli_main(argv)


__all__ = [
    "ArtifactSummary",
    "ConnectionRecord",
    "DiagramRecord",
    "DuplicateArtifactIdError",
    "EntityRecord",
    "ModelRepository",
    "RepoMount",
    "SearchHit",
    "SearchResult",
    "SemanticSearchProvider",
    "main",
]


if __name__ == "__main__":
    import sys

    sys.exit(main())
