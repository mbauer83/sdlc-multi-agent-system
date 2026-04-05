from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

from src.tools import model_write_ops
from src.tools.model_mcp.context import RepoPreset, RepoScope, registry_cached, resolve_repo_roots, roots_key, verifier_for, clear_caches_for_repo


WriteRepoScope = model_write_ops.WriteRepoScope
DiagramConnectionInferenceMode = model_write_ops.DiagramConnectionInferenceMode


def model_write_help() -> dict[str, object]:
    return model_write_ops.write_help()


def model_create_entity(
    *,
    artifact_type: str,
    name: str,
    phase_produced: str,
    owner_agent: str,
    produced_by_skill: str,
    summary: str | None = None,
    properties: dict[str, str] | None = None,
    notes: str | None = None,
    domain: str | None = None,
    safety_relevant: bool = False,
    artifact_id: str | None = None,
    version: str = "0.1.0",
    status: str = "draft",
    last_updated: str | None = None,
    dry_run: bool = True,
    repo_root: str | None = None,
    repo_preset: RepoPreset | None = None,
    repo_scope: WriteRepoScope = "engagement",
) -> dict[str, object]:
    if repo_scope != "engagement":
        raise ValueError("model_create_entity only supports repo_scope='engagement'")

    roots = resolve_repo_roots(
        repo_scope="engagement",
        repo_root=repo_root,
        repo_preset=repo_preset,
        enterprise_root=None,
    )
    key = roots_key(roots)
    registry = registry_cached(key)
    verifier = verifier_for(key, include_registry=False)

    result = model_write_ops.create_entity(
        repo_root=roots[0],
        registry=registry,
        verifier=verifier,
        clear_repo_caches=clear_caches_for_repo,
        artifact_type=artifact_type,
        name=name,
        phase_produced=phase_produced,
        owner_agent=owner_agent,
        produced_by_skill=produced_by_skill,
        summary=summary,
        properties=properties,
        notes=notes,
        domain=domain,
        safety_relevant=safety_relevant,
        artifact_id=artifact_id,
        version=version,
        status=status,
        last_updated=last_updated,
        dry_run=dry_run,
    )

    out: dict[str, object] = {
        "dry_run": dry_run,
        "wrote": bool(result.wrote),
        "path": str(result.path),
        "artifact_id": result.artifact_id,
        "verification": result.verification,
    }
    if result.content is not None:
        out["content"] = result.content
    if result.warnings:
        out["warnings"] = result.warnings
    return out


def model_create_connection(
    *,
    artifact_type: str,
    source: str | list[str],
    target: str | list[str],
    phase_produced: str,
    owner_agent: str,
    summary: str | None = None,
    display: dict[str, object] | None = None,
    version: str = "0.1.0",
    status: str = "draft",
    last_updated: str | None = None,
    dry_run: bool = True,
    repo_root: str | None = None,
    repo_preset: RepoPreset | None = None,
    repo_scope: WriteRepoScope = "engagement",
) -> dict[str, object]:
    if repo_scope != "engagement":
        raise ValueError("model_create_connection only supports repo_scope='engagement'")

    roots = resolve_repo_roots(
        repo_scope="engagement",
        repo_root=repo_root,
        repo_preset=repo_preset,
        enterprise_root=None,
    )
    key = roots_key(roots)
    registry = registry_cached(key)
    verifier = verifier_for(key, include_registry=True)

    result = model_write_ops.create_connection(
        repo_root=roots[0],
        registry=registry,
        verifier=verifier,
        clear_repo_caches=clear_caches_for_repo,
        artifact_type=artifact_type,
        source=source,
        target=target,
        phase_produced=phase_produced,
        owner_agent=owner_agent,
        summary=summary,
        display=display,
        version=version,
        status=status,
        last_updated=last_updated,
        dry_run=dry_run,
    )

    out: dict[str, object] = {
        "dry_run": dry_run,
        "wrote": bool(result.wrote),
        "path": str(result.path),
        "artifact_id": result.artifact_id,
        "verification": result.verification,
    }
    if result.content is not None:
        out["content"] = result.content
    if result.warnings:
        out["warnings"] = result.warnings
    return out


def model_create_diagram(
    *,
    diagram_type: str,
    name: str,
    purpose: str,
    puml: str,
    phase_produced: str,
    owner_agent: str,
    artifact_id: str | None = None,
    domain: str | None = None,
    version: str = "0.1.0",
    status: str = "draft",
    infer_entity_ids: bool = True,
    connection_inference: DiagramConnectionInferenceMode = "auto",
    entity_ids_used: list[str] | None = None,
    connection_ids_used: list[str] | None = None,
    auto_include_macros: bool = True,
    auto_include_stereotypes: bool = True,
    dry_run: bool = True,
    repo_root: str | None = None,
    repo_preset: RepoPreset | None = None,
    repo_scope: WriteRepoScope = "engagement",
) -> dict[str, object]:
    if repo_scope != "engagement":
        raise ValueError("model_create_diagram only supports repo_scope='engagement'")

    roots = resolve_repo_roots(
        repo_scope="engagement",
        repo_root=repo_root,
        repo_preset=repo_preset,
        enterprise_root=None,
    )
    key = roots_key(roots)
    registry = registry_cached(key)
    verifier = verifier_for(key, include_registry=True)

    result = model_write_ops.create_diagram(
        repo_root=roots[0],
        registry=registry,
        verifier=verifier,
        clear_repo_caches=clear_caches_for_repo,
        diagram_type=diagram_type,
        name=name,
        purpose=purpose,
        puml=puml,
        phase_produced=phase_produced,
        owner_agent=owner_agent,
        artifact_id=artifact_id,
        domain=domain,
        version=version,
        status=status,
        infer_entity_ids=infer_entity_ids,
        connection_inference=connection_inference,
        entity_ids_used=entity_ids_used,
        connection_ids_used=connection_ids_used,
        auto_include_macros=auto_include_macros,
        auto_include_stereotypes=auto_include_stereotypes,
        dry_run=dry_run,
    )

    out: dict[str, object] = {
        "dry_run": dry_run,
        "wrote": bool(result.wrote),
        "path": str(result.path),
        "artifact_id": result.artifact_id,
        "verification": result.verification,
    }
    if result.content is not None:
        out["content"] = result.content
    if result.warnings:
        out["warnings"] = result.warnings
    return out


def register_write_tools(mcp: FastMCP) -> None:
    mcp.tool(
        name="model_write_help",
        title="Model Write: Help & Catalog",
        description=(
            "Return the authoritative catalog of entity/connection types and key conventions for deterministic writing. "
            "Use this before calling model_create_entity/model_create_connection/model_create_diagram. "
            "All lists are derived from code registries (src/common/archimate_types.py) and server mapping tables."
        ),
        structured_output=True,
    )(model_write_help)

    mcp.tool(
        name="model_create_entity",
        title="Model Write: Create Entity",
        description=(
            "Create or update a model-entity file deterministically, with verifier-gated writes. "
            "If dry_run=true, returns the would-be path/content and verification results without writing. "
            "Repo selection must point at an engagement work-repository; enterprise writes are refused."
        ),
        structured_output=True,
    )(model_create_entity)

    mcp.tool(
        name="model_create_connection",
        title="Model Write: Create Connection",
        description=(
            "Create or update a model-connection file deterministically, with verifier-gated writes. "
            "Constructs artifact-id from source/target and writes to connections/<lang>/<dir>/. "
            "If dry_run=true, returns would-be path/content and verification results without writing."
        ),
        structured_output=True,
    )(model_create_connection)

    mcp.tool(
        name="model_create_diagram",
        title="Model Write: Create Diagram",
        description=(
            "Create or update a diagram .puml file deterministically. "
            "Caller supplies PUML body; server writes/updates the PUML frontmatter header and runs verification. "
            "Supports dry_run for safe iteration."
        ),
        structured_output=True,
    )(model_create_diagram)
