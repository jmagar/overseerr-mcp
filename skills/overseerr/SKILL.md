---
name: overseerr
description: This skill should be used when the user says "request movie", "request TV show", "get something on Plex", "search Overseerr", "request media", "submit media request", "check request status", "has my request been approved", "is X available yet", "list failed requests", "approve this request", "decline this request", "what's trending on Plex", "what movies are coming out", "recommend something similar to X", "show me my Plex watchlist", "what's my request quota", "check playback data", "there's an issue with this show", "report a problem with this movie", or mentions Overseerr, TMDB IDs, Radarr/Sonarr request management, or managing a Plex media library. Also appropriate when the user discovers a movie or show during research and wants to request it, or needs to manage, approve, troubleshoot, browse, delete, or update media requests.
---

# Overseerr Skill

## Setup

Credentials: `~/.config/overseerr-mcp/.env` (or `~/.config/overseerr-mcp/.env`). Run the `config-media-stack` skill to configure automatically.

```bash
OVERSEERR_URL="https://overseerr.example.com"
OVERSEERR_API_KEY="<your_api_key>"
```

- `OVERSEERR_URL`: Your Overseerr server URL (no trailing slash)
- `OVERSEERR_API_KEY`: API key from Overseerr Settings → General → API Key

## Mode Detection

**MCP mode** (preferred): Use when `mcp__overseerr-mcp__*` tools are available. The overseerr-mcp server runs as an HTTP service; its URL is configured via `overseerr_mcp_url` in the plugin config UI (default: `http://overseerr-mcp:9151`).

**HTTP fallback mode**: Use when MCP tools are not loaded. Use `bash skills/overseerr/scripts/overseerr-api` — credentials are loaded automatically from `~/.config/overseerr-mcp/.env` via `load-env`.

---

## MCP Mode — Tool Reference

| Tool | Parameters |
|------|-----------|
| `mcp__overseerr-mcp__search_media` | `query` (required), `media_type` ("movie"\|"tv", optional) |
| `mcp__overseerr-mcp__get_movie_details` | `tmdb_id` (required) |
| `mcp__overseerr-mcp__request_movie` | `tmdb_id` (required) |
| `mcp__overseerr-mcp__get_tv_show_details` | `tmdb_id` (required) |
| `mcp__overseerr-mcp__request_tv_show` | `tmdb_id` (required), `seasons` (optional list e.g. [1,2,3] — omit for all) |
| `mcp__overseerr-mcp__list_failed_requests` | `count` (optional, default 10), `skip` (optional, default 0) |

`search_media` returns results with `tmdbId`, `title`, `mediaType`, `year`, and current request status.

---

## Typical Workflow

1. Search with `search_media` to find TMDB ID
2. Get details with `get_movie_details` or `get_tv_show_details` to confirm and check status
3. Submit with `request_movie` or `request_tv_show`

---

## HTTP Fallback Mode

### Workflow

1. Search to find TMDB ID
2. Get details to confirm title and check if already requested
3. Submit request; use `request <id>` to check approval status afterwards

### Search
```bash
bash skills/overseerr/scripts/overseerr-api search "The Matrix"
# Raw JSON (for piping to jq):
bash skills/overseerr/scripts/overseerr-api search-json "The Matrix"
```

### Get details
```bash
bash skills/overseerr/scripts/overseerr-api movie 603
bash skills/overseerr/scripts/overseerr-api tv 1399
```

### Request media
```bash
bash skills/overseerr/scripts/overseerr-api request-movie 603
bash skills/overseerr/scripts/overseerr-api request-tv 1399               # all seasons
bash skills/overseerr/scripts/overseerr-api request-tv 1399 --season 1 --season 2
```

### List failed requests
```bash
bash skills/overseerr/scripts/overseerr-api failed-requests
bash skills/overseerr/scripts/overseerr-api failed-requests --take 20 --skip 20
bash skills/overseerr/scripts/overseerr-api failed-requests --sort modified
```

### Check a specific request
```bash
bash skills/overseerr/scripts/overseerr-api request <request-id>
```

Use this to check whether a submitted request has been approved, pending, or failed.

For the full command list — including `requests`, `approve`, `decline`, `discover-movies`, `trending`, `users`, `issues`, and more — see **[Quick Reference](./references/quick-reference.md)**.

---

## Notes

- Always search first — never guess `tmdb_id` values
- Always check details before requesting to avoid duplicates
- TV show requests default to all seasons if `--season` is omitted
- Failed requests may indicate download or availability issues — report to user with titles
- `approve`, `decline`, `retry`, and `update-request` are script-only — there are no MCP equivalents for these operations; switch to HTTP fallback mode when managing requests

---

## Reference

- **[Capability Map](./references/capability-map.md)** — Full MCP vs script coverage table
- **[Quick Reference](./references/quick-reference.md)** — Copy-paste examples for every command
- **[Troubleshooting](./references/troubleshooting.md)** — Auth failures, duplicate requests, connection errors

---

## Agent Tool Usage Requirements

When running script commands via the zsh tool, always pass `pty: true` — without it, command output will be suppressed even though the command executes successfully.
