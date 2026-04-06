# Deployment — overseerr-mcp

## Docker Compose (recommended)

### Quick start

```bash
cp .env.example .env
# Edit .env with your Overseerr credentials and MCP token
just up
```

### docker-compose.yml

The compose file configures:

- **Image:** Built from local `Dockerfile`
- **Port:** `${OVERSEERR_MCP_PORT:-9151}:${OVERSEERR_MCP_PORT:-9151}`
- **Network:** External network `${DOCKER_NETWORK:-overseerr-mcp}`
- **User:** `${PUID:-1000}:${PGID:-1000}`
- **Memory limit:** 1024 MB
- **CPU limit:** 1 core
- **Healthcheck:** `wget -qO- http://127.0.0.1:${OVERSEERR_MCP_PORT:-9151}/health`
- **Restart policy:** `unless-stopped`
- **Env file:** `~/.claude-homelab/.env` (optional, falls back to local `.env`)
- **Volume:** `${APPDATA_PATH:-./data}/overseerr-mcp:/app/data`

### Data directories

```bash
bash bin/setup-data-dirs.sh
```

Creates `${APPDATA_PATH}/overseerr-mcp/logs` with correct ownership.

## Dockerfile

Multi-stage build:

1. **Builder stage** (`python:3.11-slim`):
   - Installs `uv` from `ghcr.io/astral-sh/uv:0.10.10`
   - Copies `pyproject.toml` and `uv.lock` for dependency layer caching
   - Installs production dependencies with `uv sync --frozen --no-dev`

2. **Runtime stage** (`python:3.11-slim`):
   - Creates `mcpuser` (UID 1000)
   - Copies venv and source from builder
   - Installs `wget` for healthchecks
   - Exposes port 9151
   - Runs as `mcpuser`

### Build manually

```bash
just build
# or: docker build -t overseerr-mcp .
```

## Entrypoint

`entrypoint.sh` validates required environment variables before starting:

1. Checks `OVERSEERR_MCP_TOKEN` is set (unless `OVERSEERR_MCP_NO_AUTH=true`)
2. Exits with error message if token is missing
3. Runs `python3 -m overseerr_mcp.server`

## Reverse proxy (SWAG)

A SWAG nginx subdomain config is included at `docs/overseerr.subdomain.conf`. Configure your SWAG instance to proxy to the MCP server.

## Production checklist

- [ ] `OVERSEERR_MCP_TOKEN` set to a strong random token
- [ ] `OVERSEERR_URL` uses `https://`
- [ ] Container runs on an external Docker network (`mcp-net`)
- [ ] Volume mounts use absolute paths
- [ ] Log volume is writable by UID 1000
- [ ] Healthcheck passes: `just health`

## Operations

```bash
just up        # start in background
just down      # stop
just restart   # restart
just logs      # tail logs
just health    # check /health endpoint
```
