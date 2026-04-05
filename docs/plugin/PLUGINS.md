# Plugin Manifests — overseerr-mcp

## Claude Code (.claude-plugin/plugin.json)

Primary plugin manifest for Claude Code.

| Field | Value |
| --- | --- |
| `name` | `overseerr-mcp` |
| `version` | `1.0.1` |
| `description` | Overseerr media requests via MCP tools with HTTP fallback |
| `author` | Jacob Magar |
| `repository` | https://github.com/jmagar/overseerr-mcp |
| `license` | MIT |
| `keywords` | overseerr, media, requests, plex, mcp |

### userConfig

| Key | Type | Sensitive | Default | Description |
| --- | --- | --- | --- | --- |
| `overseerr_mcp_url` | string | no | `https://overseerr.tootie.tv/mcp` | MCP server URL |
| `overseerr_mcp_token` | string | yes | — | Bearer token for MCP auth |
| `overseerr_url` | string | yes | — | Overseerr server URL |
| `overseerr_api_key` | string | yes | — | Overseerr API key |

## Codex (.codex-plugin/plugin.json)

| Field | Value |
| --- | --- |
| `name` | `overseerr-mcp` |
| `version` | `1.0.1` |
| `interface.displayName` | Overseerr MCP |
| `interface.shortDescription` | Search media and submit Overseerr requests |
| `interface.category` | Media |
| `interface.capabilities` | Read, Write |
| `interface.brandColor` | `#F59E0B` |
| `skills` | `./skills/` |
| `mcpServers` | `./.mcp.json` |
| `apps` | `./.app.json` |

## Gemini (gemini-extension.json)

| Field | Value |
| --- | --- |
| `name` | `overseerr-mcp` |
| `version` | `1.0.1` |
| `mcpServers.overseerr-mcp.command` | `uv` |
| `mcpServers.overseerr-mcp.args` | `["run", "overseerr-mcp-server"]` |
| `settings` | `OVERSEERR_URL`, `OVERSEERR_API_KEY` |

## MCP client (.mcp.json)

```json
{
  "mcpServers": {
    "overseerr-mcp": {
      "type": "http",
      "url": "${OVERSEERR_MCP_URL}"
    }
  }
}
```

## App metadata (.app.json)

```json
{
  "name": "overseerr-mcp",
  "version": "1.0.0",
  "description": "Overseerr media request management via MCP"
}
```
