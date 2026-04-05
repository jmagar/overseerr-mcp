# Skills — overseerr-mcp

## Skill: overseerr

**Location:** `skills/overseerr/SKILL.md`

### Frontmatter

```yaml
name: overseerr
description: >
  This skill should be used when the user says "request movie", "request TV show",
  "add to Plex", "search Overseerr", "request media", "find movie", "find TV show",
  "what's available on Plex", "submit media request", "get movie details",
  "get TV show details", "list failed requests", or mentions Overseerr, Plex media
  requests, or wanting to watch something.
```

### Mode detection

The skill detects two modes:

1. **MCP mode** (preferred): When `mcp__overseerr-mcp__*` tools are available
2. **HTTP fallback mode**: When MCP tools are not loaded, uses `curl` with `$CLAUDE_PLUGIN_OPTION_OVERSEERR_URL` and `$CLAUDE_PLUGIN_OPTION_OVERSEERR_API_KEY`

### MCP tools referenced

| Tool | Parameters |
| --- | --- |
| `mcp__overseerr-mcp__search_media` | `query` (required), `media_type` (optional) |
| `mcp__overseerr-mcp__get_movie_details` | `tmdb_id` (required) |
| `mcp__overseerr-mcp__get_tv_show_details` | `tmdb_id` (required) |
| `mcp__overseerr-mcp__request_movie` | `tmdb_id` (required) |
| `mcp__overseerr-mcp__request_tv_show` | `tmdb_id` (required), `seasons` (optional) |
| `mcp__overseerr-mcp__list_failed_requests` | `count` (optional), `skip` (optional) |

### HTTP fallback examples

The skill includes curl examples for all operations in HTTP fallback mode, using the Overseerr REST API directly at `/api/v1/`.

### Key notes in skill

- Always search first — never guess TMDB IDs
- Check details before requesting to avoid duplicates
- TV requests default to all seasons if `seasons` omitted
- Failed requests may indicate Radarr/Sonarr download issues
