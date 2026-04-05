from __future__ import annotations

from typing import Any, Literal

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

from src.tools.model_mcp.context import RepoPreset, RepoScope, resolve_repo_roots, roots_key, verifier_for
from src.tools.model_mcp.formatting import as_verification_result_dict


def model_verify_file(
    path: str,
    *,
    file_type: Literal["entity", "connection", "diagram"] | None = None,
    include_registry: bool = True,
    repo_root: str | None = None,
    repo_preset: RepoPreset | None = None,
    enterprise_root: str | None = None,
    repo_scope: RepoScope = "both",
) -> dict[str, Any]:
    roots = resolve_repo_roots(
        repo_scope=repo_scope,
        repo_root=repo_root,
        repo_preset=repo_preset,
        enterprise_root=enterprise_root,
    )
    key = roots_key(roots)
    engagement_root = roots[0]

    from pathlib import Path

    p = Path(path).expanduser()
    if not p.is_absolute():
        p = engagement_root / p

    inferred = file_type
    if inferred is None:
        if p.suffix == ".puml" or (p.suffix == ".md" and "diagram-catalog" in p.parts and "diagrams" in p.parts):
            inferred = "diagram"
        else:
            inferred = "connection" if "connections" in p.parts else "entity"

    verifier = verifier_for(key, include_registry=include_registry)
    match inferred:
        case "entity":
            result = verifier.verify_entity_file(p)
        case "connection":
            result = verifier.verify_connection_file(p)
        case "diagram":
            if p.suffix == ".md":
                result = verifier.verify_matrix_diagram_file(p)
            else:
                result = verifier.verify_diagram_file(p)

    out = as_verification_result_dict(result)
    out["repo_roots"] = [str(r) for r in roots]
    out["repo_scope"] = repo_scope
    return out


def model_verify_all(
    *,
    include_diagrams: bool = True,
    include_registry: bool = True,
    return_mode: Literal["summary", "full"] = "summary",
    repo_root: str | None = None,
    repo_preset: RepoPreset | None = None,
    enterprise_root: str | None = None,
    repo_scope: RepoScope = "both",
) -> dict[str, Any]:
    roots = resolve_repo_roots(
        repo_scope=repo_scope,
        repo_root=repo_root,
        repo_preset=repo_preset,
        enterprise_root=enterprise_root,
    )
    key = roots_key(roots)
    engagement_root = roots[0]

    verifier = verifier_for(key, include_registry=include_registry)
    results = verifier.verify_all(engagement_root, include_diagrams=include_diagrams)

    total = len(results)
    total_valid = sum(1 for r in results if r.valid)
    total_errors = sum(len(r.errors) for r in results)
    total_warnings = sum(len(r.warnings) for r in results)

    if return_mode == "full":
        payload: Any = [as_verification_result_dict(r) for r in results]
    else:
        payload = [
            {
                "path": str(r.path),
                "file_type": r.file_type,
                "valid": r.valid,
                "issues": [
                    {"severity": i.severity, "code": i.code, "message": i.message, "location": i.location}
                    for i in r.issues
                ],
            }
            for r in results
            if r.issues
        ]

    return {
        "repo_roots": [str(r) for r in roots],
        "repo_scope": repo_scope,
        "include_diagrams": include_diagrams,
        "include_registry": include_registry,
        "counts": {
            "files": total,
            "valid_files": total_valid,
            "invalid_files": total - total_valid,
            "errors": total_errors,
            "warnings": total_warnings,
        },
        "results": payload,
    }


def register_verify_tools(mcp: FastMCP) -> None:
    mcp.tool(
        name="model_verify_file",
        title="Model Verifier: Verify One File",
        description=(
            "Verify a single entity/connection/diagram file under an architecture repository. "
            "If include_registry=true (default), cross-file reference checks run using a ModelRegistry." 
            "\n\nArguments: path may be absolute or relative to repo_root. file_type can be provided or inferred." 
            "\n\nRepo selection: repo_scope defaults to both (engagement + enterprise)."
        ),
        structured_output=True,
    )(model_verify_file)

    mcp.tool(
        name="model_verify_all",
        title="Model Verifier: Verify Repo",
        description=(
            "Batch-verify all model-entities/, connections/, and (optionally) diagram files under repo_root. "
            "return_mode='summary' returns counts + issues only; 'full' returns per-file issue lists." 
            "\n\nRepo selection: repo_scope defaults to both (engagement + enterprise)."
        ),
        structured_output=True,
    )(model_verify_all)
