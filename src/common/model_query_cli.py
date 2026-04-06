from __future__ import annotations

import sys
import textwrap
from pathlib import Path
from typing import Any

from src.common.model_query_types import ConnectionRecord, DiagramRecord, EntityRecord

USAGE = """\
Usage: python -m src.common.model_query <subcommand> [options]

Subcommands:
  stats     [--repo PATH]
      Print counts by layer and connection language.

  entities  [--repo PATH] [--layer LAYER] [--type TYPE] [--agent AGENT]
            [--phase PHASE] [--status STATUS] [--safety-relevant]
      List entities matching the given filters.

  connections [--repo PATH] [--lang LANG] [--type TYPE] [--agent AGENT]
              [--source ID] [--target ID]
      List connections matching the given filters.

  diagrams  [--repo PATH] [--type TYPE] [--agent AGENT] [--phase PHASE]
      List diagrams matching the given filters.

  get       [--repo PATH] ID
      Print full details for an entity, connection, or diagram.

  graph     [--repo PATH] [--hops N] [--lang LANG] ID
      Show connections and N-hop neighbors for an entity.

  search    [--repo PATH] [--limit N] [--layer LAYER] [--entities-only]
            [--connections] [--diagrams] QUERY...
      Keyword-score all records against QUERY.

Defaults:
  --repo    engagements/ENG-001/work-repositories/architecture-repository
  --limit   10
  --hops    1
"""


def repo_from_args(args: list[str]) -> tuple[Path, list[str]]:
    if "--repo" in args:
        idx = args.index("--repo")
        repo = Path(args[idx + 1])
        args = args[:idx] + args[idx + 2 :]
    else:
        repo = Path("engagements/ENG-001/work-repositories/architecture-repository")
    return repo, args


def flag(args: list[str], arg_name: str) -> tuple[str | None, list[str]]:
    if arg_name in args:
        idx = args.index(arg_name)
        value = args[idx + 1] if idx + 1 < len(args) else None
        return value, args[:idx] + args[idx + 2 :]
    return None, args


def bool_flag(args: list[str], arg_name: str) -> tuple[bool, list[str]]:
    if arg_name in args:
        return True, [arg for arg in args if arg != arg_name]
    return False, args


def fmt_entity(rec: EntityRecord, *, verbose: bool = False) -> str:
    lines = [str(rec)]
    if verbose:
        if rec.content_text:
            lines.append(textwrap.indent(rec.content_text[:400], "    "))
        if rec.display_blocks:
            for lang, block in rec.display_blocks.items():
                lines.append(f"    [{lang}]: {block[:100].replace(chr(10), ' ')}")
    return "\n".join(lines)


def fmt_connection(rec: ConnectionRecord, *, verbose: bool = False) -> str:
    lines = [str(rec)]
    if verbose and rec.content_text:
        lines.append(textwrap.indent(rec.content_text[:300], "    "))
    return "\n".join(lines)


def fmt_diagram(rec: DiagramRecord, *, verbose: bool = False) -> str:
    lines = [str(rec)]
    if verbose:
        if rec.entity_ids_used:
            lines.append(f"    entities used: {', '.join(rec.entity_ids_used)}")
        if rec.connection_ids_used:
            lines.append(f"    connections used: {', '.join(rec.connection_ids_used)}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    from src.common.model_query import ModelRepository

    args = list(argv if argv is not None else sys.argv[1:])
    if not args or args[0] in ("-h", "--help"):
        print(USAGE)
        return 0

    subcommand = args[0]
    args = args[1:]
    repo, args = repo_from_args(args)
    if not repo.exists():
        print(f"Error: repository path does not exist: {repo}", file=sys.stderr)
        return 1

    registry = ModelRepository(repo)
    dispatch = {
        "stats": _cmd_stats,
        "entities": _cmd_entities,
        "connections": _cmd_connections,
        "diagrams": _cmd_diagrams,
        "get": _cmd_get,
        "graph": _cmd_graph,
        "search": _cmd_search,
    }
    handler = dispatch.get(subcommand)
    if handler is None:
        print(f"Unknown subcommand: {subcommand}\n{USAGE}", file=sys.stderr)
        return 1
    return handler(registry, args)


def _cmd_stats(registry: Any, args: list[str]) -> int:
    del args
    stats = registry.stats()
    entities_by_layer = stats.get("entities_by_layer", {})
    connections_by_lang = stats.get("connections_by_lang", {})

    print(f"Repository: {registry.repo_root}")
    print(f"  Entities:    {stats['entities']}")
    print(f"  Connections: {stats['connections']}")
    print(f"  Diagrams:    {stats['diagrams']}")
    print("  Entities by layer:")
    for layer, count in sorted(_safe_items(entities_by_layer)):
        print(f"    {layer:20s} {count}")
    print("  Connections by language:")
    for lang, count in sorted(_safe_items(connections_by_lang)):
        print(f"    {lang:20s} {count}")
    return 0


def _cmd_entities(registry: Any, args: list[str]) -> int:
    layer_val, args = flag(args, "--layer")
    type_val, args = flag(args, "--type")
    agent_val, args = flag(args, "--agent")
    phase_val, args = flag(args, "--phase")
    status_val, args = flag(args, "--status")
    safe_flag, args = bool_flag(args, "--safety-relevant")
    verbose_flag, args = bool_flag(args, "--verbose")
    recs = registry.list_entities(
        artifact_type=type_val,
        layer=layer_val,
        owner_agent=agent_val,
        phase_produced=phase_val,
        status=status_val,
        safety_relevant=True if safe_flag else None,
    )
    print(f"{len(recs)} entities")
    for rec in recs:
        print(fmt_entity(rec, verbose=verbose_flag))
    return 0


def _cmd_connections(registry: Any, args: list[str]) -> int:
    lang_val, args = flag(args, "--lang")
    type_val, args = flag(args, "--type")
    agent_val, args = flag(args, "--agent")
    src_val, args = flag(args, "--source")
    tgt_val, args = flag(args, "--target")
    verbose_flag, args = bool_flag(args, "--verbose")
    recs = registry.list_connections(
        conn_lang=lang_val,
        conn_type=type_val,
        owner_agent=agent_val,
        source=src_val,
        target=tgt_val,
    )
    print(f"{len(recs)} connections")
    for rec in recs:
        print(fmt_connection(rec, verbose=verbose_flag))
    return 0


def _cmd_diagrams(registry: Any, args: list[str]) -> int:
    type_val, args = flag(args, "--type")
    agent_val, args = flag(args, "--agent")
    phase_val, args = flag(args, "--phase")
    status_val, args = flag(args, "--status")
    verbose_flag, args = bool_flag(args, "--verbose")
    recs = registry.list_diagrams(
        diagram_type=type_val,
        owner_agent=agent_val,
        phase_produced=phase_val,
        status=status_val,
    )
    print(f"{len(recs)} diagrams")
    for rec in recs:
        print(fmt_diagram(rec, verbose=verbose_flag))
    return 0


def _cmd_get(registry: Any, args: list[str]) -> int:
    if not args:
        print("Usage: get ID", file=sys.stderr)
        return 1
    artifact_id = args[0]
    rec = registry.get_entity(artifact_id) or registry.get_connection(artifact_id) or registry.get_diagram(artifact_id)
    if rec is None:
        print(f"Not found: {artifact_id}")
        return 1
    if isinstance(rec, EntityRecord):
        print(fmt_entity(rec, verbose=True))
    elif isinstance(rec, ConnectionRecord):
        print(fmt_connection(rec, verbose=True))
    else:
        print(fmt_diagram(rec, verbose=True))
    return 0


def _cmd_graph(registry: Any, args: list[str]) -> int:
    hops_str, args = flag(args, "--hops")
    lang_val, args = flag(args, "--lang")
    max_hops = int(hops_str) if hops_str else 1
    if not args:
        print("Usage: graph [--hops N] [--lang LANG] ID", file=sys.stderr)
        return 1
    entity_id = args[0]
    entity = registry.get_entity(entity_id)
    if entity is None:
        print(f"Entity not found: {entity_id}")
        return 1

    print(f"Graph for {entity_id}: {entity.name}")
    print()
    print("Direct connections:")
    _print_direct_connections(registry, entity_id=entity_id, lang_val=lang_val)
    if max_hops > 1:
        _print_neighbors(registry, entity_id=entity_id, max_hops=max_hops, lang_val=lang_val)
    return 0


def _print_direct_connections(registry: Any, *, entity_id: str, lang_val: str | None) -> None:
    conns = registry.find_connections_for(entity_id, conn_lang=lang_val)
    if not conns:
        print("  (none)")
        return
    for conn in conns:
        print(_format_connection_edge(conn, entity_id=entity_id))


def _format_connection_edge(conn: ConnectionRecord, *, entity_id: str) -> str:
    direction = "OUT" if entity_id in conn.source_ids else "IN "
    other = ", ".join(conn.target_ids) if direction == "OUT" else ", ".join(conn.source_ids)
    return f"  [{direction}] {conn.conn_type:20s} → {other}  ({conn.artifact_type})"


def _print_neighbors(registry: Any, *, entity_id: str, max_hops: int, lang_val: str | None) -> None:
    neighbors = registry.find_neighbors(entity_id, max_hops=max_hops, conn_lang=lang_val)
    for hop, nids in sorted(neighbors.items(), key=lambda x: int(x[0])):
        print(f"\nHop {hop} neighbors:")
        for nid in sorted(nids):
            n = registry.get_entity(nid)
            label = n.name if n else nid
            print(f"  {nid}: {label}")


def _cmd_search(registry: Any, args: list[str]) -> int:
    limit_str, args = flag(args, "--limit")
    layer_val, args = flag(args, "--layer")
    entities_only, args = bool_flag(args, "--entities-only")
    include_conns, args = bool_flag(args, "--connections")
    include_diags, args = bool_flag(args, "--diagrams")
    limit = int(limit_str) if limit_str else 10
    query = " ".join(args)
    if not query:
        print("Usage: search [options] QUERY...", file=sys.stderr)
        return 1

    result = registry.search(
        query,
        limit=limit,
        layers=[layer_val] if layer_val else None,
        include_connections=False if entities_only else (include_conns or not entities_only),
        include_diagrams=False if entities_only else (include_diags or not entities_only),
    )
    print(result)
    return 0


def _safe_items(value: object) -> list[tuple[str, int]]:
    if isinstance(value, dict):
        out: list[tuple[str, int]] = []
        for key, count in value.items():
            out.append((str(key), int(count)))
        return out
    return []
