# Plugin Configuration — overseerr-mcp

## userConfig (Claude Code)

Configured when installing the plugin via Claude Code. Values are interpolated into `.mcp.json` via `${userConfig.*}` references — no sync scripts or `.env` files needed.

| Key | Type | Sensitive | Description |
| --- | --- | --- | --- |
| `overseerr_url` | string | yes | Base URL of your Overseerr server (no trailing slash) |
| `overseerr_api_key` | string | yes | Overseerr API key (Settings > General > API Key) |

## How it works

1. `plugin.json` declares `"mcpServers": "./.mcp.json"` — Claude Code reads this on install.
2. `.mcp.json` defines the stdio command and env vars. Sensitive vars use `${userConfig.overseerr_url}` / `${userConfig.overseerr_api_key}` interpolation.
3. Claude Code prompts the user for each `userConfig` field and substitutes the values at spawn time.
4. The server starts via stdio — no HTTP listener, no bearer token needed.

## Settings (Gemini)

Configured through the Gemini extension settings UI.

| Setting | Env var | Sensitive | Description |
| --- | --- | --- | --- |
| Overseerr URL | `OVERSEERR_URL` | no | URL of the Overseerr instance |
| Overseerr API Key | `OVERSEERR_API_KEY` | yes | API key from Overseerr Settings |

## Docker / HTTP deployment

For Docker or HTTP deployments, credentials go in `.env` alongside `docker-compose.yaml`:

```bash
cp .env.example .env
chmod 600 .env
```

See [CONFIG.md](../CONFIG.md) for the full environment variable reference.
