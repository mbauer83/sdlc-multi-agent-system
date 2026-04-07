from __future__ import annotations

import sys
import textwrap
from pathlib import Path
from typing import Callable
from typing import Literal

from .index import FrameworkKnowledgeIndex
from .types import ReferenceDirection


def usage() -> str:
    return textwrap.dedent(
        """\
        Usage: python -m src.common.framework_query <subcommand> [options]

        Subcommands:
          stats [--root PATH]
          list [--root PATH] [--owner OWNER] [--tag TAG] [--path-prefix PREFIX]
          search [--root PATH] [--limit N] [--doc-id ID] QUERY...
          read [--root PATH] [--section ID_OR_HEADING] [--mode summary|full] DOC_ID_OR_PATH
          related [--root PATH] [--limit N] DOC_ID_OR_PATH
          neighbors [--root PATH] [--section ID_OR_HEADING] [--direction out|in|both] DOC_ID_OR_PATH
          path [--root PATH] [--hops N] SOURCE_REF TARGET_REF
          refresh [--root PATH]
        """
    )


def flag(args: list[str], name: str) -> tuple[str | None, list[str]]:
    if name not in args:
        return None, args
    idx = args.index(name)
    value = args[idx + 1] if idx + 1 < len(args) else None
    return value, args[:idx] + args[idx + 2 :]


def root_from_args(args: list[str]) -> tuple[Path, list[str]]:
    root_val, args = flag(args, "--root")
    root = Path(root_val) if root_val is not None else Path(".")
    return root, args


def parse_direction(value: str | None) -> ReferenceDirection:
    if value == "out":
        return "out"
    if value == "in":
        return "in"
    return "both"


def cmd_stats(index: FrameworkKnowledgeIndex, args: list[str]) -> int:
    del args
    stats = index.stats()
    print(f"Root: {index.root}")
    print(f"Docs: {stats.docs}")
    print(f"Sections: {stats.sections}")
    print(f"References: {stats.references}")
    return 0


def cmd_list(index: FrameworkKnowledgeIndex, args: list[str]) -> int:
    owner, args = flag(args, "--owner")
    tag, args = flag(args, "--tag")
    path_prefix, args = flag(args, "--path-prefix")
    recs = index.list_docs(owner=owner, tag=tag, path_prefix=path_prefix)
    print(f"{len(recs)} docs")
    for rec in recs:
        rel = rec.path.relative_to(index.root)
        print(f"[{rec.doc_id}] {rel} ({rec.section_count} sections)")
    return 0


def cmd_search(index: FrameworkKnowledgeIndex, args: list[str]) -> int:
    limit_str, args = flag(args, "--limit")
    doc_id, args = flag(args, "--doc-id")
    query = " ".join(args)
    if not query:
        print("search requires QUERY", file=sys.stderr)
        return 1
    limit = int(limit_str) if limit_str is not None else 10
    hits = index.search_docs(query, limit=limit, doc_id=doc_id)
    print(f"{len(hits)} hits")
    for hit in hits:
        sec = hit.section
        print(
            f"score={hit.score:.1f} [{sec.doc_id}#{sec.section_id}] "
            f"{sec.path.relative_to(index.root)}:{sec.line_start}"
        )
        print(f"  {hit.snippet}")
    return 0


def cmd_read(index: FrameworkKnowledgeIndex, args: list[str]) -> int:
    section, args = flag(args, "--section")
    mode_val, args = flag(args, "--mode")
    mode: Literal["summary", "full"] = "full" if mode_val == "full" else "summary"
    if not args:
        print("read requires DOC_ID_OR_PATH", file=sys.stderr)
        return 1
    print(index.read_doc(args[0], section=section, mode=mode))
    return 0


def cmd_related(index: FrameworkKnowledgeIndex, args: list[str]) -> int:
    limit_str, args = flag(args, "--limit")
    if not args:
        print("related requires DOC_ID_OR_PATH", file=sys.stderr)
        return 1
    limit = int(limit_str) if limit_str is not None else 5
    recs = index.related_docs(args[0], limit=limit)
    for rec in recs:
        print(f"[{rec.doc_id}] {rec.path.relative_to(index.root)}")
    return 0


def cmd_neighbors(index: FrameworkKnowledgeIndex, args: list[str]) -> int:
    section, args = flag(args, "--section")
    direction, args = flag(args, "--direction")
    if not args:
        print("neighbors requires DOC_ID_OR_PATH", file=sys.stderr)
        return 1
    edges = index.neighbors(args[0], section=section, direction=parse_direction(direction))
    for edge in edges:
        print(f"{edge.source_node_id} -> {edge.target_node_id} ({edge.target_path})")
    return 0


def cmd_path(index: FrameworkKnowledgeIndex, args: list[str]) -> int:
    hops_str, args = flag(args, "--hops")
    if len(args) < 2:
        print("path requires SOURCE_REF TARGET_REF", file=sys.stderr)
        return 1
    hops = int(hops_str) if hops_str is not None else 6
    edges = index.trace_path(args[0], args[1], max_hops=hops)
    if not edges:
        print("(no path)")
        return 0
    for edge in edges:
        print(f"{edge.source_node_id} -> {edge.target_node_id}")
    return 0


def cmd_refresh(index: FrameworkKnowledgeIndex, args: list[str]) -> int:
    del args
    index.refresh()
    stats = index.stats()
    print(f"Refreshed {stats.docs} docs / {stats.sections} sections / {stats.references} refs")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    if not args or args[0] in {"-h", "--help"}:
        print(usage())
        return 0

    subcommand = args[0]
    args = args[1:]
    root, args = root_from_args(args)
    index = FrameworkKnowledgeIndex(root.resolve())

    dispatch: dict[str, Callable[[FrameworkKnowledgeIndex, list[str]], int]] = {
        "stats": cmd_stats,
        "list": cmd_list,
        "search": cmd_search,
        "read": cmd_read,
        "related": cmd_related,
        "neighbors": cmd_neighbors,
        "path": cmd_path,
        "refresh": cmd_refresh,
    }
    handler = dispatch.get(subcommand)
    if handler is None:
        print(f"Unknown subcommand: {subcommand}\n{usage()}", file=sys.stderr)
        return 1
    return handler(index, args)
