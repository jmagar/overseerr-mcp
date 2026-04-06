# Environment Variables — overseerr-mcp

Complete reference for all environment variables read by the server.

## Deployment paths

| Path | Transport | Credentials source | Auth |
| --- | --- | --- | --- |
| **Plugin (stdio)** | `stdio` | `${userConfig.*}` in `.mcp.json` | None (no HTTP layer) |
| **Docker (HTTP)** | `streamable-http` | `.env` file | Bearer token (`OVERSEERR_MCP_TOKEN`) |

For plugin deployment, see [Plugin Configuration](../plugin/CONFIG.md).

## Loading order

1. `python-dotenv` loads `.env` from the project root (`load_dotenv(override=True)`)
2. System/container environment variables (overridden by .env due to `override=True`)
3. For plugin/stdio: env vars are passed directly by Claude Code via `.mcp.json` — they are already in `process.env` before `dotenv` loads, and `dotenv` with `override=True` will overwrite them only if a `.env` file exists

## Required variables

| Variable | Type | Description |
| --- | --- | --- |
| `OVERSEERR_URL` | string | Base URL of Overseerr instance (e.g. `https://overseerr.example.com`). No trailing slash. |
| `OVERSEERR_API_KEY` | string | Overseerr API key (Settings > General > API Key). |

The server exits at startup if either is missing.

## MCP server variables

| Variable | Type | Default | Description |
| --- | --- | --- | --- |
| `OVERSEERR_MCP_TRANSPORT` | string | `streamable-http` | `streamable-http`, `http`, `stdio`, or `sse` |
| `OVERSEERR_MCP_HOST` | string | `0.0.0.0` | Network interface to bind |
| `OVERSEERR_MCP_PORT` | integer | `6975` | HTTP server port (`.env.example` uses `9151`) |
| `OVERSEERR_MCP_TOKEN` | string | `""` | Bearer token for MCP auth |
| `OVERSEERR_MCP_NO_AUTH` | boolean | `false` | Disable bearer auth |

## Safety variables

| Variable | Type | Default | Description |
| --- | --- | --- | --- |
| `OVERSEERR_MCP_ALLOW_DESTRUCTIVE` | boolean | `false` | Reserved for future use |
| `OVERSEERR_MCP_ALLOW_YOLO` | boolean | `false` | Reserved for future use |

## Logging variables

| Variable | Type | Default | Description |
| --- | --- | --- | --- |
| `OVERSEERR_LOG_LEVEL` | string | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `LOG_LEVEL` | string | `INFO` | Fallback if `OVERSEERR_LOG_LEVEL` not set |

Log file: `logs/overseerr_mcp.log` — rotating, 5 MB max, 3 backups.

## Docker variables

| Variable | Type | Default | Description |
| --- | --- | --- | --- |
| `PUID` | integer | `1000` | UID for container process |
| `PGID` | integer | `1000` | GID for container process |
| `DOCKER_NETWORK` | string | `mcp-net` | External Docker network name |
| `APPDATA_PATH` | string | `/mnt/appdata` | Host path for persistent data volumes |

## Dockerfile defaults

The Dockerfile sets these defaults in the runtime stage:

```dockerfile
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    OVERSEERR_MCP_HOST=0.0.0.0 \
    OVERSEERR_MCP_PORT=9151 \
    OVERSEERR_MCP_TRANSPORT=http
```

Note: the Dockerfile default port is `9151`, while the Python code default is `6975`. The Dockerfile value takes precedence in container deployments.
