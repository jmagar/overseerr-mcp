# Plugin Configuration — overseerr-mcp

## userConfig (Claude Code)

Configured when installing the plugin via Claude Code. Values are synced to `.env` by the `sync-env.sh` hook.

| Key | Type | Sensitive | Default | Description |
| --- | --- | --- | --- | --- |
| `overseerr_mcp_url` | string | no | `https://overseerr.tootie.tv/mcp` | URL of the MCP server |
| `overseerr_mcp_token` | string | yes | — | Bearer token for MCP auth |
| `overseerr_url` | string | yes | — | Overseerr server URL |
| `overseerr_api_key` | string | yes | — | Overseerr API key |

## Settings (Gemini)

Configured through the Gemini extension settings UI.

| Setting | Env var | Sensitive | Description |
| --- | --- | --- | --- |
| Overseerr URL | `OVERSEERR_URL` | no | URL of the Overseerr instance |
| Overseerr API Key | `OVERSEERR_API_KEY` | yes | API key from Overseerr Settings |

## Environment variable sync

The `sync-env.sh` hook maps plugin userConfig to `.env` variables:

```
CLAUDE_PLUGIN_OPTION_OVERSEERR_URL      → OVERSEERR_URL
CLAUDE_PLUGIN_OPTION_OVERSEERR_API_KEY  → OVERSEERR_API_KEY
CLAUDE_PLUGIN_OPTION_OVERSEERR_MCP_URL  → OVERSEERR_MCP_URL
CLAUDE_PLUGIN_OPTION_OVERSEERR_MCP_TOKEN → OVERSEERR_MCP_TOKEN
```

The hook runs at session start and creates/updates `.env` with file locking and backups.

## Manual configuration

For non-plugin deployments, copy `.env.example` to `.env` and edit directly:

```bash
cp .env.example .env
chmod 600 .env
```

See [CONFIG.md](../CONFIG.md) for the full environment variable reference.
