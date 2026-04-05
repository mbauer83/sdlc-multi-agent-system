from __future__ import annotations

import threading
import time
from pathlib import Path

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

from src.tools.model_mcp.context import RepoPreset, RepoScope, clear_caches_for_repo, resolve_repo_roots


def _repo_mtime_fingerprint(repo_path: Path) -> float:
    max_mtime = 0.0
    for sub in ("model-entities", "connections", "diagram-catalog/diagrams"):
        root = repo_path / sub
        if not root.exists():
            continue
        for p in root.rglob("*"):
            try:
                if p.is_file():
                    max_mtime = max(max_mtime, p.stat().st_mtime)
            except OSError:
                continue
    return max_mtime


def _roots_mtime_fingerprint(roots: list[Path]) -> float:
    return max((_repo_mtime_fingerprint(r) for r in roots), default=0.0)


def _roots_key(roots: list[Path]) -> str:
    return "|".join(str(p.resolve()) for p in roots)


_watch_lock = threading.Lock()
_watch_threads: dict[str, threading.Thread] = {}
_watch_stop: dict[str, threading.Event] = {}
_watch_state: dict[str, dict[str, object]] = {}


def _watcher_loop(roots: list[Path], interval_s: float, stop: threading.Event) -> None:
    repo_key = _roots_key(roots)
    last_fp = _roots_mtime_fingerprint(roots)
    with _watch_lock:
        _watch_state[repo_key] = {
            "repo_roots": [str(r) for r in roots],
            "interval_s": interval_s,
            "running": True,
            "last_fingerprint": last_fp,
            "last_refresh_time": None,
            "refresh_count": 0,
        }

    while not stop.is_set():
        time.sleep(interval_s)
        fp = _roots_mtime_fingerprint(roots)
        if fp != last_fp:
            clear_caches_for_repo(roots[0])
            last_fp = fp
            with _watch_lock:
                st = _watch_state.get(repo_key, {})
                st["last_fingerprint"] = fp
                st["last_refresh_time"] = time.time()
                prev = st.get("refresh_count", 0)
                st["refresh_count"] = (prev + 1) if isinstance(prev, int) else 1
                _watch_state[repo_key] = st

    with _watch_lock:
        st = _watch_state.get(repo_key, {})
        st["running"] = False
        _watch_state[repo_key] = st


def register_watch_tools(mcp: FastMCP) -> None:
    @mcp.tool(
        name="model_tools_refresh",
        title="Model Tools: Refresh Index",
        description=(
            "Force a re-scan/re-index/re-cache for the selected repository. "
            "Use this after you update any entity/connection/diagram files, or from a periodic task." 
            "\n\nRepo selection: repo_scope defaults to both (engagement + enterprise)."
        ),
        structured_output=True,
    )
    def model_tools_refresh(
        *,
        repo_root: str | None = None,
        repo_preset: RepoPreset | None = None,
        enterprise_root: str | None = None,
        repo_scope: RepoScope = "both",
    ) -> dict[str, object]:
        roots = resolve_repo_roots(
            repo_scope=repo_scope,
            repo_root=repo_root,
            repo_preset=repo_preset,
            enterprise_root=enterprise_root,
        )
        clear_caches_for_repo(roots[0])
        return {
            "repo_roots": [str(p) for p in roots],
            "repo_scope": repo_scope,
            "refreshed": True,
        }

    @mcp.tool(
        name="model_tools_watch_start",
        title="Model Tools: Watch Repo",
        description=(
            "Start a lightweight polling watcher that refreshes caches whenever files under model-entities/, connections/, "
            "or diagram-catalog/diagrams change. Intended for dev usage when you don’t have an external watcher." 
            "\n\nFor large repositories, prefer an external filesystem watcher and call model_tools_refresh periodically." 
            "\n\nRepo selection: repo_scope defaults to both (engagement + enterprise)."
        ),
        structured_output=True,
    )
    def model_tools_watch_start(
        *,
        interval_s: float = 2.0,
        repo_root: str | None = None,
        repo_preset: RepoPreset | None = None,
        enterprise_root: str | None = None,
        repo_scope: RepoScope = "both",
    ) -> dict[str, object]:
        roots = resolve_repo_roots(
            repo_scope=repo_scope,
            repo_root=repo_root,
            repo_preset=repo_preset,
            enterprise_root=enterprise_root,
        )
        repo_key = _roots_key(roots)

        with _watch_lock:
            if repo_key in _watch_threads and _watch_threads[repo_key].is_alive():
                return {"repo_root": repo_key, "started": False, "reason": "already_running"}

            fp = _roots_mtime_fingerprint(roots)
            _watch_state[repo_key] = {
                "repo_roots": [str(r) for r in roots],
                "interval_s": interval_s,
                "running": True,
                "last_fingerprint": fp,
                "last_refresh_time": None,
                "refresh_count": 0,
            }
            stop = threading.Event()
            t = threading.Thread(
                target=_watcher_loop,
                args=(roots, interval_s, stop),
                daemon=True,
                name=f"model-repo-watch:{repo_key}",
            )
            _watch_stop[repo_key] = stop
            _watch_threads[repo_key] = t
            t.start()
            state = dict(_watch_state.get(repo_key, {}))

        return {"repo_roots": [str(r) for r in roots], "started": True, "state": state}

    @mcp.tool(
        name="model_tools_watch_status",
        title="Model Tools: Watch Status",
        description=(
            "Return watcher status for the selected repository (if started)." 
            "\n\nRepo selection: repo_scope defaults to both (engagement + enterprise)."
        ),
        structured_output=True,
    )
    def model_tools_watch_status(
        *,
        repo_root: str | None = None,
        repo_preset: RepoPreset | None = None,
        enterprise_root: str | None = None,
        repo_scope: RepoScope = "both",
    ) -> dict[str, object]:
        roots = resolve_repo_roots(
            repo_scope=repo_scope,
            repo_root=repo_root,
            repo_preset=repo_preset,
            enterprise_root=enterprise_root,
        )
        repo_key = _roots_key(roots)
        with _watch_lock:
            thread = _watch_threads.get(repo_key)
            state = dict(_watch_state.get(repo_key, {}))
        return {
            "repo_roots": [str(r) for r in roots],
            "running": bool(thread and thread.is_alive()),
            "state": state,
        }

    @mcp.tool(
        name="model_tools_watch_stop",
        title="Model Tools: Stop Watch",
        description=(
            "Stop the polling watcher (if running) for the selected repository." 
            "\n\nRepo selection: repo_scope defaults to both (engagement + enterprise)."
        ),
        structured_output=True,
    )
    def model_tools_watch_stop(
        *,
        repo_root: str | None = None,
        repo_preset: RepoPreset | None = None,
        enterprise_root: str | None = None,
        repo_scope: RepoScope = "both",
    ) -> dict[str, object]:
        roots = resolve_repo_roots(
            repo_scope=repo_scope,
            repo_root=repo_root,
            repo_preset=repo_preset,
            enterprise_root=enterprise_root,
        )
        repo_key = _roots_key(roots)
        with _watch_lock:
            stop = _watch_stop.get(repo_key)
            t = _watch_threads.get(repo_key)
        if stop is None or t is None:
            return {"repo_roots": [str(r) for r in roots], "stopped": False, "reason": "not_running"}
        stop.set()
        t.join(timeout=1.0)
        with _watch_lock:
            running = bool(t.is_alive())
            st = dict(_watch_state.get(repo_key, {}))
            st["running"] = running
            _watch_state[repo_key] = st
        return {"repo_roots": [str(r) for r in roots], "stopped": True, "running": running}
