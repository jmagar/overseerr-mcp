---
name: overseerr
description: This skill should be used when the user says "request movie", "request TV show", "add to Plex", "search Overseerr", "request media", "find movie", "find TV show", "what's available on Plex", "submit media request", "get movie details", "get TV show details", "list failed requests", or mentions Overseerr, Plex media requests, or wanting to watch something. Also appropriate when the user discovers a movie or show during research and wants to request it.
---

# Overseerr Skill

## Mode Detection

**MCP mode** (preferred): Use when `mcp__overseerr-mcp__*` tools are available. These tools communicate with the overseerr-mcp server which handles all Overseerr API auth internally.

**HTTP fallback mode**: Use when MCP tools are not loaded. Credentials available as `$CLAUDE_PLUGIN_OPTION_OVERSEERR_URL` and `$CLAUDE_PLUGIN_OPTION_OVERSEERR_API_KEY` in Bash subprocesses.

**MCP URL**: `${user_config.overseerr_mcp_url}`

---

## MCP Mode — Tool Reference

### Search

```
mcp__overseerr-mcp__search_media
  query       (required) Search query string
  media_type  (optional) "movie" or "tv" — omit to search both
```

Returns list of results with `tmdbId`, `title`, `mediaType`, `year`, and current request status.

### Movie Details & Requests

```
mcp__overseerr-mcp__get_movie_details
  tmdb_id  (required) TMDB integer ID from search results

mcp__overseerr-mcp__request_movie
  tmdb_id  (required) TMDB integer ID
```

### TV Show Details & Requests

```
mcp__overseerr-mcp__get_tv_show_details
  tmdb_id  (required) TMDB integer ID from search results

mcp__overseerr-mcp__request_tv_show
  tmdb_id  (required) TMDB integer ID
  seasons  (optional) List of season numbers to request, e.g. [1, 2, 3]
           Omit to request all seasons
```

### Failed Requests

```
mcp__overseerr-mcp__list_failed_requests
  count  (optional) Number of results to return (default 10)
  skip   (optional) Offset for pagination (default 0)
```

---

## Typical Workflow

1. Search with `search_media` to find TMDB ID
2. Get details with `get_movie_details` or `get_tv_show_details` to confirm and check status
3. Submit with `request_movie` or `request_tv_show`

---

## HTTP Fallback Mode

Use when MCP tools are unavailable. Retrieve credentials first:

```bash
echo "$CLAUDE_PLUGIN_OPTION_OVERSEERR_API_KEY"
```

### Search
```bash
curl -s "$CLAUDE_PLUGIN_OPTION_OVERSEERR_URL/api/v1/search?query=$QUERY" \
  -H "X-Api-Key: $CLAUDE_PLUGIN_OPTION_OVERSEERR_API_KEY"
```

### Request a movie
```bash
curl -s -X POST "$CLAUDE_PLUGIN_OPTION_OVERSEERR_URL/api/v1/request" \
  -H "X-Api-Key: $CLAUDE_PLUGIN_OPTION_OVERSEERR_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"mediaType\":\"movie\",\"mediaId\":$TMDB_ID}"
```

### Request a TV show (all seasons)
```bash
curl -s -X POST "$CLAUDE_PLUGIN_OPTION_OVERSEERR_URL/api/v1/request" \
  -H "X-Api-Key: $CLAUDE_PLUGIN_OPTION_OVERSEERR_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"mediaType\":\"tv\",\"mediaId\":$TMDB_ID,\"seasons\":\"all\"}"
```

### List failed requests
```bash
curl -s "$CLAUDE_PLUGIN_OPTION_OVERSEERR_URL/api/v1/request?filter=failed&take=10" \
  -H "X-Api-Key: $CLAUDE_PLUGIN_OPTION_OVERSEERR_API_KEY"
```

---

## Notes

- `tmdb_id` values come from search results — always search first, never guess IDs
- Check `get_movie_details` / `get_tv_show_details` before requesting to avoid duplicate requests
- TV show requests default to all seasons if `seasons` is omitted
- Failed requests may indicate download or availability issues — report to user with titles
