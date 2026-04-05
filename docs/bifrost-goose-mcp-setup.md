# Bifrost + Goose + SDLC Agents MCP (Dev Setup)

This guide shows two ways to register and run the SDLC Agents “model tools” MCP server with **bifrost** (docker-compose) and **goose**.

The MCP server you built in this repo exposes:
- model query tools (list/search/read, graph helpers)
- model verification tools

Entry point:
- `uv run sdlc-mcp-model`

Default repo mounting behavior:
- mounts **both** the engagement architecture repo (ENG-001 by default) and `enterprise-repository/`
- `repo_scope` tool argument can restrict to `engagement` or `enterprise`

## 0) What you need

- Docker + docker-compose (for bifrost)
- This repo checked out locally (the “project you’re working on”)
- A place to edit bifrost’s config (often a YAML/JSON file or env var) to register MCP servers

## 1) Recommended (container-friendly): run MCP as its own compose service (Streamable HTTP)

This avoids the common container problem where bifrost cannot reliably spawn a stdio subprocess that lives outside its image/filesystem.

This guide now defaults to **Streamable HTTP** transport.

### 1.1 Build the MCP server image

From this repo root:

```bash
docker build -f tools/docker/mcp-model/Dockerfile -t sdlc-mcp-model:dev .
```

### 1.2 Add override services in bifrost’s docker-compose

In the bifrost directory (where `docker-compose.yml` lives), create a `docker-compose.override.yml` and add a service similar to:

```yaml
services:
  sdlc_mcp_model:
    image: sdlc-mcp-model:dev
    container_name: sdlc_mcp_model
    environment:
      SDLC_MCP_TRANSPORT: streamable-http
      SDLC_MCP_HOST: 0.0.0.0
      SDLC_MCP_PORT: 8000
      # Optional: make the advertised MCP server name deterministic
      SDLC_MCP_SERVER_NAME: sdlc_model
      # Optional: override default engagement repo root inside the container
      # SDLC_MCP_MODEL_REPO_ROOT: /app/engagements/ENG-001/work-repositories/architecture-repository
    ports:
      - "8000:8000"
    # If you want live-edit behavior without rebuilds, mount your working copy:
    # volumes:
    #   - /ABS/PATH/TO/sdlc-agents:/app

  sdlc_mcp_registry:
    image: sdlc-mcp-registry:dev
    container_name: sdlc_mcp_registry
    environment:
      SDLC_MCP_TRANSPORT: streamable-http
      SDLC_MCP_HOST: 0.0.0.0
      SDLC_MCP_PORT: 8001
      SDLC_MCP_SERVER_NAME: sdlc_registry
      SDLC_MCP_AGENTS_ROOT: /app/agents
    ports:
      - "8001:8001"
    # If you want live-edit behavior for agent/skill markdown without rebuilds:
    # volumes:
    #   - /ABS/PATH/TO/sdlc-agents/agents:/app/agents:ro

  bifrost:
    depends_on:
      - sdlc_mcp_model
      - sdlc_mcp_registry
```

Notes:
- FastMCP Streamable HTTP endpoint is `http://sdlc_mcp_model:8000/mcp` by default.
- Registry Streamable HTTP endpoint is `http://sdlc_mcp_registry:8001/mcp` by default.
- If you mount your repo into `/app`, your edits will be visible **immediately in the filesystem**, but:
  - The running MCP server process will **not hot-reload** Python code. You must restart the container to pick up code changes.
  - You must ensure the Python environment isn’t stored under `/app` (otherwise the bind mount hides it). The provided Dockerfile sets `UV_PROJECT_ENVIRONMENT=/opt/uv-venv` specifically so `volumes: - /ABS/PATH/TO/sdlc-agents:/app` works.

### Live-edit behavior: model files vs server code

There are two kinds of “live edits”, and they behave differently:

1. **Editing model artifacts** (entity/connection/diagram files under `engagements/.../work-repositories/...`)
  - You do **not** need to rebuild the image.
  - You do **not** need to restart the container **if** the MCP server watcher is running (or you call `model_tools_refresh`).
  - Requirement: the files must be visible inside the container (bind mount `/app`, or otherwise sync/copy them).

2. **Editing the MCP server code itself** (Python under `src/`)
  - You do **not** need to rebuild the image if you bind-mount `/app`.
  - You **do** need to restart the container so Python reloads the code.

Practical dev loop:
- Edit code in your workspace
- `docker compose restart sdlc_mcp_model`
- Goose/bifrost immediately see updated tool behavior

If you’re mostly editing model artifacts and want “automatic refresh”, enable auto-watch:

```yaml
services:
  sdlc_mcp_model:
    environment:
      SDLC_MCP_AUTO_WATCH: "1"
      SDLC_MCP_WATCH_INTERVAL: "2.0"   # polling interval seconds
      SDLC_MCP_REPO_SCOPE: "both"      # engagement|enterprise|both
      # Optional, if enterprise repo lives elsewhere inside container:
      # SDLC_MCP_ENTERPRISE_ROOT: /app/enterprise-repository
```

With auto-watch enabled, edits to bind-mounted model files trigger a cache refresh automatically; the *next* MCP tool call will see the updated index.

### 1.3 Register the MCP servers in bifrost

You need to tell bifrost “there is an MCP server named X at URL Y”. The exact config shape depends on bifrost, but it’s usually one of:

- a config file listing MCP servers, e.g.
  - `mcpServers: { <name>: { url: "http://.../sse" } }`
- an environment variable containing JSON/YAML
- a folder of server definitions

Use:
- **Model tools**
  - Name: `sdlc_model`
  - URL: `http://sdlc_mcp_model:8000/mcp`
- **Agent/skill registry**
  - Name: `sdlc_registry`
  - URL: `http://sdlc_mcp_registry:8001/mcp`

Tip:
- Keep MCP server registration names **hyphen-free** (prefer `snake_case`). Some OpenAI-tool bridges normalize names, and lossy normalization can lead to `Tool not found` at call time.

If you need to force the MCP server’s self-advertised name (handshake) to match your bifrost registration name, set:
- `SDLC_MCP_SERVER_NAME=sdlc_model` (model)
- `SDLC_MCP_SERVER_NAME=sdlc_registry` (registry)

Once registered, bifrost should expose these tools to goose.

### 1.4 Run

From the bifrost directory:

```bash
docker compose up --build
```

## 2) Alternative: SSE MCP server (only if your MCP client requires it)

If your MCP client stack only supports SSE, set:
- `SDLC_MCP_TRANSPORT=sse`
- Use URLs:
  - `http://sdlc_mcp_model:8000/sse`
  - `http://sdlc_mcp_registry:8001/sse`

## 3) Alternative: stdio MCP server spawned by bifrost (only if bifrost supports it)

This is viable if:
- bifrost supports “command” style MCP servers (spawn a subprocess and speak stdio)
- the bifrost container has Python 3.12 + `uv` available OR you run bifrost on the host
- the container can see your project directory

Example registration conceptually:
- command: `uv`
- args: `["run", "sdlc-mcp-model"]`
- cwd: `/workspace/sdlc-agents` (bind-mounted into container)

This mode avoids HTTP ports but is more fragile in docker-compose because you are mixing process management and host mounts.

## 4) Pointing goose at the right place

Since goose uses bifrost, you generally want:
- goose points to bifrost (whatever base URL/socket goose uses)
- bifrost has the MCP server registered (either SSE URL or stdio command)

If you choose to have goose talk to MCP servers **directly** (and use bifrost only as the LLM provider), publish ports and register:
- `http://localhost:8000/mcp`
- `http://localhost:8001/mcp`

Practical tip:
- integrate once in bifrost; goose inherits the tool list.

## 5) Dev workflow optimizations

### 4.1 Fast iteration for model changes

- Use `model_tools_watch_start(interval_s=...)` during active editing, or
- call `model_tools_refresh()` from your editor/task runner after writing entity/connection/diagram files.

### 4.2 Keep enterprise + engagement consistent

- Prefer `repo_scope="both"` for normal discovery.
- Use `engagement="enterprise"` filters when you explicitly want enterprise-only results.

### 4.3 Avoid rebuild loops

If you do want the MCP server container to reflect code changes instantly:
- bind-mount the repo into `/app`
- but keep in mind you may overwrite files that were created during `docker build`

A good compromise:
- rebuild the MCP server image only when dependencies change (`pyproject.toml`)
- otherwise rely on bind mount or just restart the container.

## 6) Troubleshooting checklist

- If bifrost can’t see any tools: confirm it can reach `http://sdlc_mcp_model:8000/sse` from inside the bifrost container.
- If you are using Streamable HTTP: confirm it can reach `http://sdlc_mcp_model:8000/mcp` and `http://sdlc_mcp_registry:8001/mcp`.
- If the MCP server starts but returns 0 artifacts:
  - check `SDLC_MCP_MODEL_REPO_ROOT` and that `/app/engagements/...` exists inside the container
  - call `model_query_stats()`
- If you see a “duplicate artifact-id across mounted roots” error:
  - fix the duplication; the framework forbids the same id existing in more than one mounted root.
