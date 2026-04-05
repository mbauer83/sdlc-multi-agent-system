"""context.py — shared MCP server context for model query/verify/write tools.

Keeps mcp_model_server.py small by factoring out:
- repo root resolution
- cache keys and cached ModelRepository/ModelRegistry
- verifier construction and cache clearing

This module contains no FastMCP tool registrations.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Literal

from src.common.model_query import ModelRepository
from src.common.model_verifier import ModelRegistry, ModelVerifier


RepoPreset = Literal[
    "ENG-001-architecture",
    "enterprise-architecture",
]

RepoScope = Literal["engagement", "enterprise", "both"]


def workspace_root() -> Path:
    # .../src/tools/model_mcp/context.py -> parents[0]=model_mcp, [1]=tools, [2]=src, [3]=repo root
    return Path(__file__).resolve().parents[3]


def default_engagement_repo_root() -> Path:
    import os

    env = os.getenv("SDLC_MCP_MODEL_REPO_ROOT")
    if env:
        return Path(env).expanduser()
    return workspace_root() / "engagements" / "ENG-001" / "work-repositories" / "architecture-repository"


def default_enterprise_repo_root() -> Path:
    return workspace_root() / "enterprise-repository"


def repo_root_from_preset(preset: RepoPreset) -> Path:
    root = workspace_root()
    match preset:
        case "ENG-001-architecture":
            return root / "engagements" / "ENG-001" / "work-repositories" / "architecture-repository"
        case "enterprise-architecture":
            return root / "enterprise-repository"


def resolve_repo_root(*, repo_root: str | None, repo_preset: RepoPreset | None) -> Path:
    if repo_root:
        p = Path(repo_root).expanduser()
        if not p.is_absolute():
            p = workspace_root() / p
        return p
    if repo_preset:
        return repo_root_from_preset(repo_preset)
    p = default_engagement_repo_root()
    if not p.is_absolute():
        p = workspace_root() / p
    return p


def resolve_enterprise_repo_root(*, enterprise_root: str | None) -> Path:
    if enterprise_root:
        p = Path(enterprise_root).expanduser()
        if not p.is_absolute():
            p = workspace_root() / p
        return p
    return default_enterprise_repo_root()


def resolve_repo_roots(
    *,
    repo_scope: RepoScope,
    repo_root: str | None,
    repo_preset: RepoPreset | None,
    enterprise_root: str | None,
) -> list[Path]:
    engagement = resolve_repo_root(repo_root=repo_root, repo_preset=repo_preset)
    enterprise = resolve_enterprise_repo_root(enterprise_root=enterprise_root)
    roots: list[Path] = []
    if repo_scope in ("engagement", "both"):
        roots.append(engagement)
    if repo_scope in ("enterprise", "both"):
        roots.append(enterprise)
    return roots


def roots_key(roots: list[Path]) -> str:
    return "|".join(str(p.resolve()) for p in roots)


@lru_cache(maxsize=8)
def repo_cached(roots_key_str: str) -> ModelRepository:
    roots = [Path(p) for p in roots_key_str.split("|") if p]
    return ModelRepository(roots)


@lru_cache(maxsize=8)
def registry_cached(roots_key_str: str) -> ModelRegistry:
    roots = [Path(p) for p in roots_key_str.split("|") if p]
    return ModelRegistry(roots)


def verifier_for(roots_key_str: str, *, include_registry: bool) -> ModelVerifier:
    if include_registry:
        return ModelVerifier(registry_cached(roots_key_str))
    return ModelVerifier(None)


def clear_caches_for_repo(_: Path) -> None:
    # Simple compatibility behavior: clear all caches.
    repo_cached.cache_clear()
    registry_cached.cache_clear()


@dataclass(frozen=True)
class ResolvedRepo:
    roots: list[Path]

    @property
    def key(self) -> str:
        return roots_key(self.roots)

    @property
    def engagement_root(self) -> Path:
        return self.roots[0]
