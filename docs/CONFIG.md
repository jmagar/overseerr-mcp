# Configuration Reference — overseerr-mcp

Complete environment variable reference and configuration options.

## Environment file

```bash
cp .env.example .env
chmod 600 .env
```

Precedence (highest to lowest):
1. `.env` file in project root
2. Container environment variables (Docker `-e` flags)
3. System environment variables

## Environment variables

### Overseerr credentials

| Variable | Required | Default | Sensitive | Description |
| --- | --- | --- | --- | --- |
| `OVERSEERR_URL` | yes | — | no | Base URL of the Overseerr instance (no trailing slash) |
| `OVERSEERR_API_KEY` | yes | — | yes | Overseerr API key (Settings > General > API Key) |

### MCP server

| Variable | Required | Default | Sensitive | Description |
| --- | --- | --- | --- | --- |
| `OVERSEERR_MCP_HOST` | no | `0.0.0.0` | no | Network interface to bind |
| `OVERSEERR_MCP_PORT` | no | `6975` | no | HTTP server port (`.env.example` recommends `9151`) |
| `OVERSEERR_MCP_TOKEN` | yes* | — | yes | Bearer token for HTTP auth. Generate: `openssl rand -hex 32` |
| `OVERSEERR_MCP_TRANSPORT` | no | `streamable-http` | no | Transport mode: `streamable-http`, `http`, `stdio`, or `sse` |
| `OVERSEERR_MCP_NO_AUTH` | no | `false` | no | Disable bearer auth (only behind trusted proxy) |

*Required when transport is HTTP-based and `OVERSEERR_MCP_NO_AUTH` is not `true`.

### Logging

| Variable | Required | Default | Sensitive | Description |
| --- | --- | --- | --- | --- |
| `OVERSEERR_LOG_LEVEL` | no | `INFO` | no | `DEBUG`, `INFO`, `WARNING`, `ERROR`. `LOG_LEVEL` accepted as fallback. |

Log file: `logs/overseerr_mcp.log` (rotating, 5 MB max, 3 backups).

### Safety

| Variable | Required | Default | Sensitive | Description |
| --- | --- | --- | --- | --- |
| `OVERSEERR_MCP_ALLOW_DESTRUCTIVE` | no | `false` | no | Gate for destructive operations (reserved for future use) |
| `OVERSEERR_MCP_ALLOW_YOLO` | no | `false` | no | Bypass confirmation prompts (reserved for future use) |

### Docker / container

| Variable | Required | Default | Sensitive | Description |
| --- | --- | --- | --- | --- |
| `PUID` | no | `1000` | no | UID for container process |
| `PGID` | no | `1000` | no | GID for container process |
| `DOCKER_NETWORK` | no | `mcp-net` | no | External Docker network name |
| `APPDATA_PATH` | no | `/mnt/appdata` | no | Host path for persistent data volumes |

## Plugin userConfig

When installed as a Claude Code plugin, these fields map to `userConfig` in `.claude-plugin/plugin.json`:

```json
{
  "userConfig": {
    "overseerr_mcp_url": {
      "type": "string",
      "title": "Overseerr MCP Server URL",
      "description": "URL of the overseerr-mcp MCP server (e.g. http://overseerr-mcp:9151).",
      "default": "https://overseerr.tootie.tv/mcp",
      "sensitive": false
    },
    "overseerr_mcp_token": {
      "type": "string",
      "title": "MCP Server Bearer Token",
      "description": "Bearer token for authenticating with the MCP server.",
      "sensitive": true
    },
    "overseerr_url": {
      "type": "string",
      "title": "Overseerr Server URL",
      "description": "Base URL of your Overseerr server.",
      "sensitive": true
    },
    "overseerr_api_key": {
      "type": "string",
      "title": "Overseerr API Key",
      "description": "Overseerr API key. Found in Overseerr Settings > General > API Key.",
      "sensitive": true
    }
  }
}
```

## .env.example conventions

- Group variables by section with comment headers
- Required variables first within each group
- No actual secrets — use descriptive placeholders
- `.env.example` is tracked in git; `.env` is gitignored
