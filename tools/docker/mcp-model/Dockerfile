# MCP Model Tools server image (for bifrost/goose via SSE/HTTP)
#
# Build context should be the sdlc-agents repo root.
#
# Example:
#   docker build -f tools/docker/mcp-model/Dockerfile -t sdlc-mcp-model:dev .
#
# Run (SSE transport):
#   docker run --rm -p 8000:8000 \
#     -e SDLC_MCP_TRANSPORT=sse -e SDLC_MCP_HOST=0.0.0.0 -e SDLC_MCP_PORT=8000 \
#     sdlc-mcp-model:dev

FROM python:3.12-slim

# System deps: curl is required by the uv installer script.
# git is useful if uv needs to resolve VCS deps.
RUN apt-get update \
  && apt-get install -y --no-install-recommends ca-certificates git curl \
  && rm -rf /var/lib/apt/lists/*

# Install uv (fast, reproducible Python dependency management)
ADD https://astral.sh/uv/install.sh /tmp/uv-install.sh
RUN sh /tmp/uv-install.sh && rm /tmp/uv-install.sh
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app

# IMPORTANT for dev bind-mounts:
# If you mount your working copy onto /app, anything created under /app at build
# time (including a default .venv) can get hidden. Keep the uv environment
# outside /app so live-edit mounts don't break imports.
ENV UV_PROJECT_ENVIRONMENT=/opt/uv-venv

# Copy only dependency files first for better docker layer caching.
COPY pyproject.toml /app/pyproject.toml
# If you later add a uv.lock, copy it too for fully pinned builds:
# COPY uv.lock /app/uv.lock

# Sync deps. (If uv.lock exists, this becomes fully reproducible.)
RUN uv sync

# Now copy the source.
COPY src /app/src
COPY framework /app/framework
COPY specs /app/specs
COPY agents /app/agents
COPY engagements-config.yaml enterprise-repository-config.yaml README.md CLAUDE.md /app/
COPY engagements /app/engagements
COPY enterprise-repository /app/enterprise-repository

EXPOSE 8000

# Default to Streamable HTTP so bifrost/goose can connect over HTTP in docker-compose.
# Endpoint: http://<service>:8000/mcp
ENV SDLC_MCP_TRANSPORT=streamable-http
ENV SDLC_MCP_HOST=0.0.0.0
ENV SDLC_MCP_PORT=8000
ENV SDLC_MCP_SERVER_NAME=sdlc_model
ENV SDLC_MCP_JSON_RESPONSE=1
ENV SDLC_MCP_STATELESS_HTTP=1

CMD ["uv", "run", "sdlc-mcp-model"]
