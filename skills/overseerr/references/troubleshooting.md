# Overseerr Troubleshooting

## Authentication Errors

### `401 Unauthorized` from the script

The `OVERSEERR_API_KEY` in `~/.config/overseerr-mcp/.env` is wrong or missing.

```bash
# Verify the key is set
grep OVERSEERR_API_KEY ~/.config/overseerr-mcp/.env

# Get your API key: Overseerr → Settings → General → API Key
# Update it:
sed -i "s|^OVERSEERR_API_KEY=.*|OVERSEERR_API_KEY=newvalue|" "~/.config/overseerr-mcp/.env"
```

### MCP tools return auth errors

The `overseerr_mcp_token` in the plugin config UI must match `OVERSEERR_MCP_TOKEN` in the server's `.env`. Update both if they've drifted.

---

## Connection Errors

### `curl: (7) Failed to connect` / `unreachable`

`OVERSEERR_URL` is wrong, the server is down, or a firewall is blocking access.

```bash
# Test connectivity directly
curl -s "${OVERSEERR_URL}/api/v1/settings/about" -H "X-Api-Key: ${OVERSEERR_API_KEY}"

# Verify the URL is set correctly
grep OVERSEERR_URL ~/.config/overseerr-mcp/.env
```

Check that `OVERSEERR_URL` has no trailing slash and uses the correct port.

### MCP tools not available (no `mcp__overseerr-mcp__*` tools)

The overseerr-mcp HTTP server is not running or not reachable at the configured URL. Use HTTP fallback mode with `./skills/overseerr/scripts/overseerr-api` instead.

To check the server:
```bash
curl -s "${OVERSEERR_MCP_URL:-http://overseerr-mcp:9151}/health"
```

---

## Request Errors

### "Request already exists" / duplicate request

The media has already been requested. Check status with `get_movie_details` or `get_tv_show_details` (MCP) or `movie`/`tv` commands (script) before requesting.

### Request submitted but nothing downloads

Check that Radarr/Sonarr are connected to Overseerr (Overseerr → Settings → Services) and that the media has an approved status. Use `failed-requests` to surface items that failed at the download stage.

### `load-env not in PATH`

The plugin is not enabled or `bin/` is not on PATH. Re-enable the plugin in Claude Code settings and start a new session.

---

## Credential Setup

Run the `config-media-stack` skill to diagnose and fix credential issues:

```bash
preflight
```

This tests connectivity and auth for all 8 services and reports specific failures.
